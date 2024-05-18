from typing import Any, Optional

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger as APCronTrigger
from homecontrol_base.database.core import DatabaseConfig
from sqlalchemy_utils import create_database, database_exists

from homecontrol_api.scheduler.schemas import JobPost, Trigger, TriggerType


class Scheduler:
    """Handles an APScheduler instance for the API"""

    def __init__(self):
        database_config = DatabaseConfig()

        # Create database if it doesn't exist in case not using sqlite
        url = database_config.get_url("apscheduler")
        if not database_exists(url):
            create_database(url)

        self._scheduler = AsyncIOScheduler(
            jobstores={
                "default": SQLAlchemyJobStore(
                    url=database_config.get_url("apscheduler")
                )
            }
        )

    def start(self):
        """Start the scheduler"""
        self._scheduler.start()

    def stop(self):
        """Stop the scheduler (By default waits until all running tasks
        completed)"""
        self._scheduler.shutdown()

    def _get_trigger_args(self, trigger: Trigger) -> dict[str, Any]:
        """Returns arguments to give to APScheduler defining the trigger"""

        if trigger.trigger_type == TriggerType.DATETIME:
            return {"trigger": "date", "run_date": trigger.value}
        elif trigger.trigger_type == TriggerType.INTERVAL:
            return {
                "trigger": "interval",
                "weeks": trigger.value.weeks,
                "days": trigger.value.days,
                "hours": trigger.value.hours,
                "minutes": trigger.value.minutes,
                "seconds": trigger.value.seconds,
            }
        elif trigger.trigger_type == TriggerType.CRON:
            return {"trigger": APCronTrigger.from_crontab(trigger.value)}

    def add_job(self, job_id: str, job_info: JobPost, task_function: Any):
        """Add a job to the scheduler"""
        self._scheduler.add_job(
            func=task_function,
            id=job_id,
            args=[job_id],
            **self._get_trigger_args(job_info.trigger),
        )

    def pause_job(self, job_id: str):
        self._scheduler.pause_job(job_id=job_id)

    def resume_job(self, job_id: str):
        self._scheduler.resume_job(job_id=job_id)

    def modify_job(
        self,
        job_id: str,
        new_trigger: Optional[Trigger] = None,
    ):
        modify_args = {}
        if new_trigger:
            modify_args = {**modify_args, **self._get_trigger_args(new_trigger)}
        self._scheduler.modify_job(job_id=job_id, **modify_args)

    def has_job(self, job_id: str):
        return self._scheduler.get_job(job_id) is not None

    def remove_job(self, job_id: str):
        """Remove a job from the scheduler"""

        self._scheduler.remove_job(job_id)
