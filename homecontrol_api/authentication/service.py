import uuid
from datetime import datetime, timezone
from fastapi import Response

from homecontrol_base.exceptions import (
    DatabaseDuplicateEntryFoundError,
    DatabaseEntryNotFoundError,
)
from homecontrol_base.service.core import BaseService

from homecontrol_api.authentication.schemas import (
    InternalUserSession,
    LoginPost,
    User,
    UserAccountType,
    UserPatch,
    UserPost,
    UserSession,
)
from homecontrol_api.authentication.security import (
    generate_jwt,
    get_jwt_expiry_time,
    hash_password,
    verify_jwt,
    verify_password,
)
from homecontrol_api.config.api import APIConfig
from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.models import UserInDB, UserSessionInDB
from homecontrol_api.exceptions import AuthenticationError, UsernameAlreadyExistsError


class AuthService(BaseService[HomeControlAPIDatabaseConnection]):
    """Service for handling authentication"""

    _api_config: APIConfig

    def __init__(
        self, db_conn: HomeControlAPIDatabaseConnection, api_config: APIConfig
    ) -> None:
        super().__init__(db_conn)

        self._api_config = api_config

    def _get_user(self, user_id: str) -> User:
        """Returns a user given their ID
        Args:
            user_id (str): ID of the user

        Raises:
            DatabaseEntryNotFoundError: If the user isn't present in the database
        """
        return User.model_validate(self.db_conn.users.get(user_id))

    def create_user(self, user_info: UserPost) -> User:
        """Creates a user

        Args:
            user_info (UserPost): Data about the user to create

        Returns:
            User: Created user

        Raises:
            UsernameAlreadyExistsError: If a user with the same username
                                        already exists
        """

        # Is this the first user? - if so create an enabled admin, otherwise
        # a default account that is disabled
        first_user = self.db_conn.users.count() == 0
        account_type = UserAccountType.ADMIN if first_user else UserAccountType.DEFAULT

        # Create the database model
        user = UserInDB(
            username=user_info.username,
            hashed_password=hash_password(user_info.password),
            account_type=account_type,
            enabled=first_user,
        )
        # Add to the database
        try:
            user = self.db_conn.users.create(user)
        except DatabaseDuplicateEntryFoundError as exc:
            raise UsernameAlreadyExistsError(str(exc)) from exc

        # Return the created user
        return User.model_validate(user)

    def update_user(self, user_id: str, user_data: UserPatch) -> User:
        """Updates a user

        Args:
            user_id (str): ID of the user to update
            user_data (UserPatch): Data to update in the user
        """

        # Obtain the user
        user = self.db_conn.users.get(user_id)

        # Assign the new data
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        # Update and return the updated data
        self.db_conn.users.update(user)
        return User.model_validate(user)

    def delete_user(self, user_id: str) -> None:
        """Deletes a user

        Args:
            user_id (str): ID of the user to delete
        """
        # TODO: Delete sessions as well?
        self.db_conn.users.delete(user_id)

    def _generate_access_token(self, session_id: str) -> str:
        """Generates an access token"""
        return generate_jwt(
            payload={"session_id": str(session_id)},
            key=self._api_config.security.jwt_key,
            seconds_to_expiry=self._api_config.security.access_token_expiry,
        )

    def _get_refresh_expiry_seconds(self, long_lived: bool) -> int:
        """Returns the refresh token expiry time from the settings"""
        return (
            self._api_config.security.long_lived_refresh_token_expiry
            if long_lived
            else self._api_config.security.refresh_token_expiry
        )

    def _generate_refresh_token(self, session_id: str, long_lived: bool) -> str:
        """Generates an refresh token

        Args:
            session_id (str): ID of the session the refresh token should be
                              tied to
            long_lived (bool): Whether to take the (potentially) longer expiry
                               time
        """
        return generate_jwt(
            payload={"session_id": str(session_id)},
            key=self._api_config.security.jwt_key,
            seconds_to_expiry=self._get_refresh_expiry_seconds(long_lived),
        )

    def _create_user_session(self, user: User, long_lived: bool) -> InternalUserSession:
        """Creates a session for a given User (assumes authentication already done)

        Args:
            user (User): User to create the session for
            long_lived (bool): Whether the session should be long lived

        Returns:
            UserSession: The user's new session
        """

        session_id = uuid.uuid4()
        user_session = UserSessionInDB(
            id=session_id,
            user_id=user.id,
            access_token=self._generate_access_token(session_id),
            refresh_token=self._generate_refresh_token(
                session_id, long_lived=long_lived
            ),
            long_lived=long_lived,
            expiry_time=get_jwt_expiry_time(
                seconds_to_expiry=self._get_refresh_expiry_seconds(long_lived)
            ),
        )
        # Save in the db
        user_session = self.db_conn.user_sessions.create(user_session)
        return InternalUserSession.model_validate(user_session)

    def _assign_session_tokens(
        self, internal_user_session: InternalUserSession, response: Response
    ):
        """Assigns the access and refresh tokens to the cookies in the response

        Args:
            internal_user_session (InternalUserSession): User session with the tokens to use
            response (Response): FastAPI response (for setting cookies)
        """
        # Stored time doesn't have timezone, so add UTC here as required for cookie
        session_expire_time_utc = internal_user_session.expiry_time.replace(
            tzinfo=timezone.utc
        )
        response.set_cookie(
            key="access_token",
            value=f"Bearer {internal_user_session.access_token}",
            expires=session_expire_time_utc,
            httponly=True,
        )
        response.set_cookie(
            key="refresh_token",
            value=internal_user_session.refresh_token,
            expires=session_expire_time_utc,
            httponly=True,
        )

    def login(self, login_info: LoginPost, response: Response) -> UserSession:
        """Logs in as a given user using a username and password

        Args:
            login_info (LoginPost): User login information
            response (Response): FastAPI response (for setting cookies)

        Returns:
            UserSession: New session fot the user to use

        Raises:
            AuthenticationError: If either the username or password is wrong
        """
        # Attempt to obtain the user
        user = None
        try:
            user = self.db_conn.users.get_by_username(login_info.username)
        except DatabaseEntryNotFoundError:
            pass
        # Now verify the password
        if not user or not verify_password(login_info.password, user.hashed_password):
            raise AuthenticationError("Invalid username or password")

        # Ensure the account is active
        if not user.enabled:
            raise AuthenticationError("Account is disabled. Please contact an admin.")

        # If got here, can create a new session
        internal_user_session = self._create_user_session(
            user,
            # Don't allow admins to have long sessions
            long_lived=login_info.long_lived
            if user.account_type != UserAccountType.ADMIN
            else False,
        )
        self._assign_session_tokens(internal_user_session, response)

        return UserSession.model_validate(internal_user_session)

    def authenticate_user_session(self, access_token: str) -> UserSession:
        """Authenticate a user session using an access token

        Will validate the access token and use it to check the user has a
        valid session then return the session.

        Args:
            access_token (str): Access token of the user

        Returns:
            UserSession: A User session object

        Raises:
            AuthenticationError: If the token has expired, or is no longer
                                 valid for the session it was made for
        """
        # Verify the token
        payload = verify_jwt(access_token, self._api_config.security.jwt_key)
        # Obtain the session
        session = self.db_conn.user_sessions.get(payload["session_id"])

        # Verify the token is the one for the session
        if session.access_token != access_token:
            raise AuthenticationError("Invalid token")

        return UserSession.model_validate(session)

    def authenticate_user(self, access_token: str) -> User:
        """Authenticate a user using an access token

        Will validate the access token and use it to check the user has a
        valid session then return the user from that session while ensuring it
        is also enabled.


        Args:
            access_token (str): Access token of the user

        Returns:
            User: A User object

        Raises:
            AuthenticationError: If the token has expired, or is no longer
                                 valid for the session it was made for
        """

        user = self._get_user(
            self.authenticate_user_session(access_token=access_token).user_id
        )
        if not user.enabled:
            raise AuthenticationError("User is disabled")
        return user

    def refresh_user_session(
        self, refresh_token: str, response: Response
    ) -> UserSession:
        """Refresh a user session given a refresh token

        Will validate the refresh token and then use it to refresh the
        user session, assigning a new access and refresh token.

        Args:
            refresh_token (str): Refresh token of the user
            response (Response): FastAPI response (for setting cookies)

        Returns:
            UserSession: Updated session for the user to use

        Raises:
            AuthenticationError: If the token has expired, or is no longer
                                 valid for the session it was made for
        """

        # Verify the token
        payload = verify_jwt(refresh_token, self._api_config.security.jwt_key)
        # Obtain the session
        user_session = self.db_conn.user_sessions.get(payload["session_id"])

        # Verify the token is the one for the session
        if user_session.refresh_token != refresh_token:
            raise AuthenticationError("Invalid token")

        # If reached here - the refresh token is valid, so update the
        # access and refresh tokens with new ones
        user_session.access_token = self._generate_access_token(
            session_id=str(user_session.id)
        )
        user_session.refresh_token = self._generate_refresh_token(
            session_id=str(user_session.id), long_lived=user_session.long_lived
        )
        user_session.expiry_time = get_jwt_expiry_time(
            seconds_to_expiry=self._get_refresh_expiry_seconds(
                long_lived=user_session.long_lived
            )
        )
        self.db_conn.user_sessions.update(user_session)

        internal_user_session = InternalUserSession.model_validate(user_session)
        self._assign_session_tokens(internal_user_session, response)

        return UserSession.model_validate(internal_user_session)

    def logout(self, user_session_id: str, response: Response) -> None:
        """Invalidate a user session

        Args:
            user_session_id (str): ID of the user session to invalidate
            response (Response): FastAPI response (for removing cookies)
        """

        # Delete the session
        self.db_conn.user_sessions.delete(user_session_id=user_session_id)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

    def delete_all_expired_sessions(self) -> None:
        """Delete all expired sessions from the database"""

        self.db_conn.user_sessions.delete_sessions_expired_before(datetime.utcnow())
