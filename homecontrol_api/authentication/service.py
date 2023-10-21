import uuid
from datetime import datetime

from homecontrol_base.exceptions import DatabaseEntryNotFoundError
from homecontrol_base.service.core import BaseService

from homecontrol_api.authentication.schemas import (
    LoginPost,
    User,
    UserAccountType,
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
from homecontrol_api.exceptions import AuthenticationError


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
        return User.model_validate(self._db_conn.users.get(user_id))

    def create_user(self, user_info: UserPost) -> User:
        """Creates a user

        Args:
            user_info (UserPost): Data about the user to create

        Returns:
            User: Created user
        """

        # Is this the first user? - if so create an enabled admin, otherwise
        # a default account that is disabled
        first_user = self._db_conn.users.count() == 0
        account_type = UserAccountType.ADMIN if first_user else UserAccountType.DEFAULT

        # Create the database model
        user = UserInDB(
            username=user_info.username,
            hashed_password=hash_password(user_info.password),
            account_type=account_type,
            enabled=first_user,
        )
        # Add to the database
        user = self._db_conn.users.create(user)
        # Return the created user
        return User.model_validate(user)

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

    def _create_user_session(self, user: User, long_lived: bool) -> UserSession:
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
        user_session = self._db_conn.user_sessions.create(user_session)
        return UserSession.model_validate(user_session)

    def login(self, login_info: LoginPost) -> UserSession:
        """Logs in as a given user using a username and password

        Args:
            login_info (LoginPost): User login information

        Returns:
            UserSession: New session fot the user to use

        Raises:
            AuthenticationError: If either the username or password is wrong
        """
        # Attempt to obtain the user
        user = None
        try:
            user = self._db_conn.users.get_by_username(login_info.username)
        except DatabaseEntryNotFoundError:
            pass
        # Now verify the password
        if not user or not verify_password(login_info.password, user.hashed_password):
            raise AuthenticationError("Invalid username or password")

        # If got here, can create a new session
        return self._create_user_session(
            user,
            # Don't allow admins to have long sessions
            long_lived=login_info.long_lived
            if user.account_type != UserAccountType.ADMIN
            else False,
        )

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
        session = self._db_conn.user_sessions.get(payload["session_id"])

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

    def refresh_user_session(self, refresh_token: str) -> UserSession:
        """Refresh a user session given a refresh token

        Will validate the refresh token and then use it to refresh the
        user session, assigning a new access and refresh token.

        Args:
            refresh_token (str): Refresh token of the user

        Returns:
            UserSession: Updated session for the user to use

        Raises:
            AuthenticationError: If the token has expired, or is no longer
                                 valid for the session it was made for
        """

        # Verify the token
        payload = verify_jwt(refresh_token, self._api_config.security.jwt_key)
        # Obtain the session
        user_session = self._db_conn.user_sessions.get(payload["session_id"])

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
        user_session.expiry_time = expiry_time = get_jwt_expiry_time(
            seconds_to_expiry=self._get_refresh_expiry_seconds(
                long_lived=user_session.long_lived
            )
        )
        self._db_conn.user_sessions.update(user_session)

        return UserSession.model_validate(user_session)

    def logout(self, user_session_id: str) -> None:
        """Invalidate a user session

        Args:
            user_session_id (str): ID of the user session to invalidate
        """

        # Delete the session
        self._db_conn.user_sessions.delete(user_session_id=user_session_id)

    def delete_all_expired_sessions(self) -> None:
        """Delete all expired sessions from the database"""

        self._db_conn.user_sessions.delete_sessions_expired_before(datetime.utcnow())
