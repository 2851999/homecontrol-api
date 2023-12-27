from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from homecontrol_api.core.types import StringUUID


class Temperature(BaseModel):
    value: Optional[float]


class HistoricTemperature(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    timestamp: datetime
    value: float
    room_name: str
