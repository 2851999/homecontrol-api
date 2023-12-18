from homecontrol_base.exceptions import DatabaseDuplicateEntryFoundError
from homecontrol_base.service.core import BaseService
from pydantic import TypeAdapter

from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.models import RoomInDB
from homecontrol_api.exceptions import NameAlreadyExistsError
from homecontrol_api.rooms.schemas import Room, RoomPatch, RoomPost


class RoomService(BaseService[HomeControlAPIDatabaseConnection]):
    """Service for handling rooms"""

    def __init__(self, db_conn: HomeControlAPIDatabaseConnection) -> None:
        super().__init__(db_conn)

    def create_room(self, room_info: RoomPost) -> Room:
        """Creates a room

        Args:
            room (Room): Data about the room to create

        Returns:
            Room: Created room

        Raises:
            NameAlreadyExistsError: If a room with the same name already exists
        """

        # Create the database model
        room = RoomInDB(**room_info.model_dump())

        # Add to the database
        try:
            room = self._db_conn.rooms.create(room)
        except DatabaseDuplicateEntryFoundError as exc:
            raise NameAlreadyExistsError(str(exc)) from exc

        # Return the created room
        return Room.model_validate(room)

    def get_rooms(self) -> list[Room]:
        """Returns a list of all available rooms"""

        return TypeAdapter(list[Room]).validate_python(self._db_conn.rooms.get_all())

    def get_room(self, room_id: str) -> Room:
        """Returns a room given its id"""

        return Room.model_validate(self._db_conn.rooms.get(room_id))

    def update_room(self, room_id: str, room_data: RoomPatch) -> Room:
        """Updates a room

        Args:
            room_id (str): ID of the room to update
            room_data (RoomPatch): Data to update in the room
        """

        # Obtain the room
        room = self._db_conn.rooms.get(room_id)

        # Assign the new data
        update_data = room_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(room, key, value)

        # Update and return the updated data
        self._db_conn.rooms.update(room)
        return Room.model_validate(room)

    def delete_room(self, room_id: str) -> None:
        """Deletes a room

        Args:
            room_id (str): ID of the room to delete
        """
        self._db_conn.rooms.delete(room_id)
