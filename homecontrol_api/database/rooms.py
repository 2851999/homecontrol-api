from uuid import UUID

from homecontrol_base.database.core import DatabaseConnection
from homecontrol_base.exceptions import (
    DatabaseDuplicateEntryFoundError,
    DatabaseEntryNotFoundError,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from homecontrol_api.database.models import RoomInDB


class RoomsDBConnection(DatabaseConnection):
    """Handles RoomInDB's in the database"""

    def __init__(self, session: Session):
        super().__init__(session)

    def create(self, room: RoomInDB) -> RoomInDB:
        """Adds a RoomInDB to the database

        Args:
            room (RoomInDB): Room to add to the database

        Raises:
            DatabaseDuplicateEntryFoundError: If a room with the same name is
                                              already present in the database
        """
        self._session.add(room)
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise DatabaseDuplicateEntryFoundError(
                f"Room with the name '{room.name}' already exists"
            ) from exc
        self._session.refresh(room)
        return room

    def get(self, room_id: str) -> RoomInDB:
        """Returns RoomInDB given a room's ID

        Args:
            room_id (str): ID of the room

        Returns:
            RoomInDB: The room

        Raises:
            DatabaseEntryNotFoundError: If the room isn't found
        """

        room = (
            self._session.query(RoomInDB).filter(RoomInDB.id == UUID(room_id)).first()
        )
        if not room:
            raise DatabaseEntryNotFoundError(f"Room with id '{room_id}' was not found")
        return room

    def get_all(self) -> list[RoomInDB]:
        """Returns a list of information about all rooms"""
        return self._session.query(RoomInDB).all()

    def count(self) -> int:
        """Returns the number of rooms in the database"""
        return self._session.query(RoomInDB).count()

    def update(self, room: RoomInDB) -> None:
        """Commits changes that have already been assigned to a room"""
        self._session.commit()
        self._session.refresh(room)

    def delete(self, room_id: str):
        """Deletes a RoomInDB given the room's id

        Args:
            room_id (str): ID of the room

        Raises:
            DatabaseEntryNotFoundError: If the room isn't found
        """
        rows_deleted = (
            self._session.query(RoomInDB).filter(RoomInDB.id == UUID(room_id)).delete()
        )

        if rows_deleted == 0:
            raise DatabaseEntryNotFoundError(f"Room with id '{room_id}' was not found")

        self._session.commit()
