from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from homecontrol_api.core.types import StringUUID


class TriggerType(StrEnum):
    """Enum of available trigger types"""

    # Date trigger in APScheduler
    DATETIME = "datetime"
    # Interval trigger in APScheduler
    INTERVAL = "interval"
    # Cron trigger in APScheduler
    CRON = "cron"


class TriggerDatetime(BaseModel):
    trigger_type: Literal[TriggerType.DATETIME] = TriggerType.DATETIME
    value: datetime


class TimeDelta(BaseModel):
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0


class TriggerInterval(BaseModel):
    trigger_type: Literal[TriggerType.INTERVAL] = TriggerType.INTERVAL
    value: TimeDelta


class TriggerCron(BaseModel):
    trigger_type: Literal[TriggerType.CRON] = TriggerType.CRON
    value: str


Trigger = Annotated[
    Union[TriggerDatetime, TriggerInterval, TriggerCron],
    Field(discriminator="trigger_type"),
]


class JobStatus(StrEnum):
    """Enum of possible job status'"""

    ACTIVE = "active"
    PAUSED = "paused"


class Job(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    name: str
    task: str
    trigger: Trigger
    status: JobStatus


class JobPost(BaseModel):
    name: str
    task: str
    trigger: Trigger


class JobPatch(BaseModel):
    name: Optional[str] = None
    task: Optional[str] = None

    # TODO: For now all or nothing for simplicity
    trigger: Optional[Trigger] = None

    status: Optional[JobStatus] = None
