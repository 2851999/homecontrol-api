from typing import Optional

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

    # Read only
    indoor_temperature: float
    outdoor_temperature: float
    display_on: bool


class ACDeviceStatePost(BaseModel):
    # Read and write
    power: bool
    target_temperature: float
    operational_mode: ACDeviceMode
    fan_speed: ACDeviceFanSpeed
    swing_mode: ACDeviceSwingMode
    eco_mode: bool
    turbo_mode: bool
    fahrenheit: bool

    # Write only
    prompt_tone: bool
