from typing import Optional
from uuid import UUID

from homecontrol_base.database.core import DatabaseConnection
from homecontrol_base.exceptions import (
    DatabaseDuplicateEntryFoundError,
    DatabaseEntryNotFoundError,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from homecontrol_api.database.models import RoomActionInDB, RoomInDB


class RoomActionsDBConnection(DatabaseConnection):
    """Handles RoomActionInDB's in the database"""

    def __init__(self, session: Session):
        super().__init__(session)

    def create(self, action: RoomActionInDB) -> RoomActionInDB:
        """Adds a RoomActionInDB to the database

        Args:
            action (RoomActionInDB): Room action to add to the database

        Raises:
            DatabaseDuplicateEntryFoundError: If a room action with the same
                                     name is already present in the database
        """
        self._session.add(action)
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise DatabaseDuplicateEntryFoundError(
                f"Room Action with the name '{action.name}' already exists"
            ) from exc
        self._session.refresh(action)
        return action

    def get(self, action_id: str) -> RoomInDB:
        """Returns RoomActionInDB given a room action's ID

        Args:
            action_id (str): ID of the room action

        Returns:
            RoomActionInDB: The room action

        Raises:
            DatabaseEntryNotFoundError: If the room action isn't found
        """

        action = (
            self._session.query(RoomActionInDB)
            .filter(RoomActionInDB.id == UUID(action_id))
            .first()
        )
        if not action:
            raise DatabaseEntryNotFoundError(
                f"Room Action with id '{action_id}' was not found"
            )
        return action

    def get_all(self, room_id: Optional[str] = None) -> list[RoomActionInDB]:
        """Returns a list of information about all room actions with optional query params"""
        filters = []
        if room_id is not None:
            filters.append(RoomActionInDB.room_id == room_id)

        if len(filters) == 0:
            return self._session.query(RoomActionInDB).all()
        else:
            return self._session.query(RoomActionInDB).filter(*filters).all()

    def count(self) -> int:
        """Returns the number of room actions in the database"""
        return self._session.query(RoomActionInDB).count()

    def update(self, action: RoomActionInDB) -> None:
        """Commits changes that have already been assigned to a room action"""
        self._session.commit()
        self._session.refresh(action)

    def delete(self, action_id: str):
        """Deletes a RoomActionInDB given the room action's id

        Args:
            action_id (str): ID of the room action

        Raises:
            DatabaseEntryNotFoundError: If the room action isn't found
        """
        rows_deleted = (
            self._session.query(RoomActionInDB)
            .filter(RoomActionInDB.id == UUID(action_id))
            .delete()
        )

        if rows_deleted == 0:
            raise DatabaseEntryNotFoundError(
                f"Room Action with id '{action_id}' was not found"
            )

        self._session.commit()
