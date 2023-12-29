from enum import StrEnum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from homecontrol_api.core.types import StringUUID, UUIDString
from homecontrol_api.devices.aircon.schemas import ACDeviceStatePut


class TaskType(StrEnum):
    """Enum of available task types"""

    # Air conditioning unit state
    AC_STATE = "ac_state"
    # Broadlink action
    BROADLINK_ACTION = "broadlink_action"
    # Phillip's Hue scene
    HUE_SCENE = "hue_scene"


class TaskACState(BaseModel):
    task_type: Literal[TaskType.AC_STATE]
    device_id: StringUUID
    state: ACDeviceStatePut


class TaskBroadlinkAction(BaseModel):
    task_type: Literal[TaskType.BROADLINK_ACTION]
    device_id: StringUUID
    action_id: StringUUID


class TaskHueScene(BaseModel):
    task_type: Literal[TaskType.HUE_SCENE]
    bridge_id: StringUUID
    scene_id: StringUUID


Task = Annotated[
    Union[TaskACState, TaskBroadlinkAction, TaskHueScene],
    Field(discriminator="task_type"),
]


class RoomAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    name: str
    room_id: StringUUID
    icon: str
    tasks: list[Task]


class TaskACStatePost(BaseModel):
    task_type: Literal[TaskType.AC_STATE]
    device_id: StringUUID


TaskPost = Annotated[
    Union[TaskACStatePost, TaskBroadlinkAction, TaskHueScene],
    Field(discriminator="task_type"),
]


class RoomActionPost(BaseModel):
    name: str
    room_id: UUIDString
    icon: str
    tasks: list[TaskPost]

    @field_serializer("tasks")
    def serialize_controllers(self, tasks: list[TaskPost]):
        """Serialize controllers to dictionary when giving to the JSON field in the database"""
        return [task.model_dump() for task in tasks]
