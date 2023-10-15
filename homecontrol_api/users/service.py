import uuid

from homecontrol_base.service.core import BaseService

from homecontrol_api.config.api import APIConfig
from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.models import UserInDB, UserSessionInDB
from homecontrol_api.exceptions import AuthenticationError
from homecontrol_api.schemas import LoginPost, User, UserPost, UserSession
from homecontrol_api.users.security import generate_jwt, hash_password, verify_password


class UserService(BaseService[HomeControlAPIDatabaseConnection]):
    """Service for handling users"""

    _api_config: APIConfig

    def __init__(
        self, db_conn: HomeControlAPIDatabaseConnection, api_config: APIConfig
    ) -> None:
        super().__init__(db_conn)

        self._api_config = api_config

    def get_user(self, user_id: str) -> User:
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

        # Create the database model
        user = UserInDB(
            username=user_info.username,
            hashed_password=hash_password(user_info.password),
            account_type=user_info.account_type,
        )
        # Add to the database
        user = self._db_conn.users.create(user)
        # Return the created user
        return User.model_validate(user)

    def _create_user_session(self, user: User) -> UserSession:
        """Creates a session for a given User (assumes authentication already done)

        Args:
            user (User): User to create the session for

        Returns:
            UserSession: The user's new session
        """

        session_id = uuid.uuid4()
        user_session = UserSessionInDB(
            id=session_id,
            user_id=user.id,
            access_token=generate_jwt(
                payload={"session_id": str(session_id)},
                key=self._api_config.security.jwt_key,
                seconds_to_expire=self._api_config.security.access_token_expiry,
            ),
            refresh_token=generate_jwt(
                payload={"session_id": str(session_id)},
                key=self._api_config.security.jwt_key,
                seconds_to_expire=self._api_config.security.refresh_token_expiry,
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
        user = self._db_conn.users.get_by_username(login_info.username)
        # Now verify the password
        if not verify_password(login_info.password, user.hashed_password):
            raise AuthenticationError("Invalid password")

        # If got here, can create a new session
        return self._create_user_session(user)

    def authenticate_user(self) -> User:
        # TODO: Authenticate using the tokens - ensuring they match the ones in the database
        # for the session found in the token
        pass
