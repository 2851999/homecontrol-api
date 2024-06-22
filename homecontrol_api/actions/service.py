from homecontrol_base.exceptions import DatabaseDuplicateEntryFoundError
from homecontrol_base.hue.api.schema import Recall, ScenePut
from homecontrol_base.service.homecontrol_base import HomeControlBaseService

from homecontrol_api.actions.schemas import (
    RoomAction,
    RoomActionPatch,
    RoomActionPost,
    TaskType,
)
from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.models import RoomActionInDB
from homecontrol_api.exceptions import NameAlreadyExistsError
from homecontrol_api.service.core import BaseAPIService


class ActionService(BaseAPIService[HomeControlAPIDatabaseConnection]):
    """Service for handling actions"""

    def __init__(
        self,
        db_conn: HomeControlAPIDatabaseConnection,
        base_service: HomeControlBaseService,
    ) -> None:
        super().__init__(db_conn, base_service)

    async def create_room_action(self, action_info: RoomActionPost) -> RoomAction:
        """Creates a room action

        Args:
            action_info (RoomActionPost): Data about the room action to create

        Returns:
            RoomActionPost: Created room action

        Raises:
            NameAlreadyExistsError: If a room action with the same name already exists
        """

        # Create the database model
        action = RoomActionInDB(**action_info.model_dump())

        # Add to the database
        try:
            action = self.db_conn.room_actions.create(action)
        except DatabaseDuplicateEntryFoundError as exc:
            raise NameAlreadyExistsError(str(exc)) from exc

        # Return the created room
        return RoomAction.model_validate(action)

    def get_room_action(self, action_id: str) -> RoomAction:
        """Returns a room action given its id"""
        return RoomAction.model_validate(
            self.db_conn.room_actions.get(action_id=action_id)
        )

    def update_room_action(
        self, action_id: str, action_data: RoomActionPatch
    ) -> RoomAction:
        """Updates a room action

        Args:
            action_id (str): ID of the room action to update
            action_data (RoomActionPatch): Data to update in the room action
        """

        # Obtain the room action
        action = self.db_conn.room_actions.get(action_id)

        # Assign the new data
        update_data = action_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(action, key, value)

        # Update and return the updated data
        self.db_conn.room_actions.update(action)
        return RoomAction.model_validate(action)

    async def execute_room_action(self, action_id: str) -> None:
        """Executes a room action

        Args:
            action_id (str): Action to execute
        """

        # Action to perform
        action = self.get_room_action(action_id=action_id)

        # Execute each task in order
        for task in action.tasks:
            if task.task_type == TaskType.AC_STATE:
                # Apply the AC state
                ac_device = await self.base_service.aircon.get_device(task.device_id)
                await ac_device.set_state(task.state)
            elif task.task_type == TaskType.BROADLINK_ACTION:
                # Apply the action
                self.base_service.broadlink.play_action(
                    device_id=task.device_id, action_id=task.action_id
                )
            elif task.task_type == TaskType.HUE_SCENE:
                # Apply the scene
                bridge = self.base_service.hue.get_bridge(bridge_id=task.bridge_id)
                with bridge.connect_api() as conn:
                    conn.put_scene(
                        task.scene_id, ScenePut(recall=Recall(action="active"))
                    )

    def delete_room_action(self, action_id: str) -> None:
        """Deletes a room action

        Args:
            action_id (str): ID of the room action to delete
        """
        self.db_conn.room_actions.delete(action_id=action_id)
