from uuid import UUID

from homecontrol_base.database.core import DatabaseConnection
from homecontrol_base.exceptions import DatabaseEntryNotFoundError
from sqlalchemy.orm import Session

from homecontrol_api.database.models import UserInDB


class UsersDBConnection(DatabaseConnection):
    """Handles UserInDB's in the database"""

    def __init__(self, session: Session):
        super().__init__(session)

    def create(self, user: UserInDB) -> UserInDB:
        """Adds a UserInDB to the database"""
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user
    
    def get(self, user_id: str) -> UserInDB:
        """Returns UserInDB given a user's ID
        
        Args:
            user_id (str): ID of the user

        Returns:
            UserInDB: Info about the user

        Raises:
            DatabaseEntryNotFoundError: If the user isn't found
        """

        user = (
            self._session.query(UserInDB).filter(UserInDB.id == UUID(user_id)).first()
        )
        if not user:
            raise DatabaseEntryNotFoundError(f"User with id '{user_id}' was not found")
        return user
    
    def get_by_username(self, username: str) -> UserInDB:
        """Returns UserInDB given a user's username
        
        Args:
            username (str): Username of the user

        Returns:
            UserInDB: Info about the user

        Raises:
            DatabaseEntryNotFoundError: If the user isn't found    
        """
        user = (
            self._session.query(UserInDB).filter(UserInDB.username ==  username).first()
        )
        if not user:
            raise DatabaseEntryNotFoundError(f"User with username '{username}' was not found")
        return user
    
    def get_all(self) -> list[UserInDB]:
        """Returns a list of information about all users"""
        return self._session.query(UserInDB).all()
    
    def delete(self, user_id: str):
        """Deletes a UserInDB given the users's id

        Args:
            user_id (str): ID of the user

        Raises:
            DatabaseEntryNotFoundError: If the user isn't found
        """
        rows_deleted = (
            self._session.query(UserInDB)
            .filter(UserInDB.id == UUID(user_id))
            .delete()
        )

        if rows_deleted == 0:
            raise DatabaseEntryNotFoundError(
                f"User with id '{user_id}' was not found"
            )

        self._session.commit()
        