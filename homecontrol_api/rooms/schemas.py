from enum import StrEnum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from homecontrol_api.core.types import StringUUID


class ControlType(StrEnum):
    """Enum of available control types"""

    # Air conditioning unit
    AC = "ac"
    # Broadlink device
    BROADLINK = "broadlink"
    # Phillip's Hue room
    HUE_ROOM = "hue_room"


class ControllerAC(BaseModel):
    control_type: Literal[ControlType.AC]
    id: StringUUID


class ControllerBroadlink(BaseModel):
    control_type: Literal[ControlType.BROADLINK]
    id: StringUUID


class ControllerHueRoom(BaseModel):
    control_type: Literal[ControlType.HUE_ROOM]
    id: StringUUID
    bridge_id: StringUUID


RoomController = Annotated[
    Union[ControllerAC, ControllerBroadlink, ControllerHueRoom],
    Field(discriminator="control_type"),
]


class Room(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    name: str
    controllers: list[RoomController]


class RoomPost(BaseModel):
    name: str
    controllers: list[RoomController]

    @field_serializer("controllers")
    def serialize_controllers(self, controllers: list[RoomController]):
        """Serialize controllers to dictionary when giving to the JSON field in the database"""
        return [controller.model_dump() for controller in controllers]


class RoomPatch(BaseModel):
    name: Optional[str] = None

    # TODO: For now all or nothing for simplicity
    controllers: Optional[list[RoomController]] = None
