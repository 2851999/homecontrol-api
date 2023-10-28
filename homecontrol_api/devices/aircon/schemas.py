from pydantic import BaseModel, ConfigDict, IPvAnyAddress

from homecontrol_api.core.types import StringUUID


class ACDevice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    name: str
    ip_address: str


class ACDevicePost(BaseModel):
    name: str
    ip_address: IPvAnyAddress
