
import bcrypt
from homecontrol_base.service.core import BaseService

from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.models import UserInDB
from homecontrol_api.users.schemas import User, UserPost


class UserService(BaseService[HomeControlAPIDatabaseConnection]):
    """Service for handling users"""

    def __init__(self, db_conn: HomeControlAPIDatabaseConnection) -> None:
        super().__init__(db_conn)

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
            name=user_info.name,
            hashed_password=bcrypt.hashpw(user_info.password.encode("utf-8"), bcrypt.gensalt()),
            account_type=user_info.account_type
        )
        # Add to the database
        user = self._db_conn.users.create(user)
        # Return the created user
        return User.model_validate(user)
        