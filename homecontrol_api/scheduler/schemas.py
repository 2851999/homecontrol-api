from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_serializer

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

    @field_serializer("value")
    def serialise_value(self, value: datetime):
        return str(value)


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


class TaskType(StrEnum):
    """Enum of available task types"""

    RECORD_ALL_TEMPERATURES = "record_all_temperature"
    EXECUTE_ROOM_ACTION = "execute_room_action"


class TaskRecordAllTemperatures(BaseModel):
    task_type: Literal[TaskType.RECORD_ALL_TEMPERATURES] = (
        TaskType.RECORD_ALL_TEMPERATURES
    )


class TaskExecuteRoomAction(BaseModel):
    task_type: Literal[TaskType.EXECUTE_ROOM_ACTION] = TaskType.EXECUTE_ROOM_ACTION
    room_id: str
    action_id: str


Task = Annotated[
    Union[TaskRecordAllTemperatures, TaskExecuteRoomAction],
    Field(discriminator="task_type"),
]


class JobStatus(StrEnum):
    """Enum of possible job status'"""

    ACTIVE = "active"
    PAUSED = "paused"


class Job(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    name: str
    task: Task
    trigger: Trigger
    status: JobStatus


class JobPost(BaseModel):
    name: str
    task: Task
    trigger: Trigger


class JobPatch(BaseModel):
    name: Optional[str] = None

    # TODO: For now all or nothing for simplicity
    task: Optional[Task] = None
    trigger: Optional[Trigger] = None

    status: Optional[JobStatus] = None
