from uuid import UUID

from homecontrol_base.database.core import DatabaseConnection
from homecontrol_base.exceptions import DatabaseEntryNotFoundError
from sqlalchemy.orm import Session

from homecontrol_api.database.models import UserSessionInDB


class UserSessionsDBConnection(DatabaseConnection):
    """Handles UserInDB's in the database"""

    def __init__(self, session: Session):
        super().__init__(session)

    def create(self, user_session: UserSessionInDB) -> UserSessionInDB:
        """Adds a UserSessionInDB to the database"""
        self._session.add(user_session)
        self._session.commit()
        self._session.refresh(user_session)
        return user_session
    
    def get(self, user_session_id: str) -> UserSessionInDB:
        """Returns UserSessionInDB given a user's ID
        
        Args:
            user_session_id (str): ID of the user

        Returns:
            UserSessionInDB: Info about the user

        Raises:
            DatabaseEntryNotFoundError: If the user isn't found
        """

        user_session = (
            self._session.query(UserSessionInDB).filter(UserSessionInDB.id == UUID(user_session_id)).first()
        )
        if not user_session:
            raise DatabaseEntryNotFoundError(f"User session with id '{user_session_id}' was not found")
        return user_session
    
    def get_all(self) -> list[UserSessionInDB]:
        """Returns a list of information about all user session"""
        return self._session.query(UserSessionInDB).all()
    
    def delete(self, user_session_id: str):
        """Deletes a UserSessionInDB given the users's id

        Args:
            user_id (str): ID of the user session

        Raises:
            DatabaseEntryNotFoundError: If the user isn't found
        """
        rows_deleted = (
            self._session.query(UserSessionInDB)
            .filter(UserSessionInDB.id == UUID(UserSessionInDB))
            .delete()
        )

        if rows_deleted == 0:
            raise DatabaseEntryNotFoundError(
                f"User session with id '{user_session_id}' was not found"
            )

        self._session.commit()
        