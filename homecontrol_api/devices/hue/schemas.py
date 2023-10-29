from pydantic import BaseModel, ConfigDict

from homecontrol_api.core.types import StringUUID


class HueBridgeDiscoverInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    internalipaddress: str
    port: int


class HueBridgePost(BaseModel):
    name: str
    discover_info: HueBridgeDiscoverInfo


class HueBridge(BaseModel):
    id: StringUUID
    name: str
    ip_address: str
    port: int
