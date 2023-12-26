from pydantic import BaseModel, ConfigDict, IPvAnyAddress

from homecontrol_api.core.types import StringUUID


class BroadlinkDevice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    name: str
    ip_address: str


class BroadlinkDevicePost(BaseModel):
    name: str
    ip_address: IPvAnyAddress


class BroadlinkAction(BaseModel):
    id: StringUUID
    name: str


class BroadlinkDeviceRecordPost(BaseModel):
    name: str


class BroadlinkDevicePlaybackPost(BaseModel):
    action_id: str
