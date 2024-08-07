from homecontrol_base.aircon.state import (
    ACDeviceFanSpeed,
    ACDeviceMode,
    ACDeviceSwingMode,
)
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


class ACDeviceState(BaseModel):
    # Read and write
    power: bool
    target_temperature: float
    operational_mode: ACDeviceMode
    fan_speed: ACDeviceFanSpeed
    swing_mode: ACDeviceSwingMode
    eco_mode: bool
    turbo_mode: bool
    fahrenheit: bool
    display_on: bool

    # Read only
    indoor_temperature: float
    outdoor_temperature: float


class ACDeviceStatePut(BaseModel):
    # Read and write
    power: bool
    target_temperature: float
    operational_mode: ACDeviceMode
    fan_speed: ACDeviceFanSpeed
    swing_mode: ACDeviceSwingMode
    eco_mode: bool
    turbo_mode: bool
    fahrenheit: bool
    display_on: bool

    # Write only
    prompt_tone: bool
