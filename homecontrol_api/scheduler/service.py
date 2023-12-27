import uuid
from homecontrol_base.service.core import BaseService
from pydantic import TypeAdapter

from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.models import JobInDB
from homecontrol_api.exceptions import TaskNotFoundError
from homecontrol_api.scheduler.core import Scheduler
from homecontrol_api.scheduler.schemas import Job, JobPost
from homecontrol_api.scheduler.tasks import AVAILABLE_TASKS


class SchedulerService(BaseService[HomeControlAPIDatabaseConnection]):
    """Service for handling Scheduling"""

    _scheduler: Scheduler

    def __init__(
        self, db_conn: HomeControlAPIDatabaseConnection, scheduler: Scheduler
    ) -> None:
        super().__init__(db_conn)

        self._scheduler = scheduler

    def create_job(self, job_info: JobPost) -> Job:
        """Creates a Job

        Args:
            job (Job): Data about the Job to create

        Returns:
            Job: Created job

        Raises:
            TaskNotFoundError: If the given task doesn't exist
        """

        # Attempt to get the task function (and ensure it exists)
        task_function = AVAILABLE_TASKS.get(job_info.task)
        if task_function is None:
            raise TaskNotFoundError(f"Task '{job_info.task}' was not found")

        # Create the database model (and ensure id is created before adding)
        job = JobInDB(**job_info.model_dump(), id=uuid.uuid4())

        # Add to the scheduler
        self._scheduler.add_job(
            job_id=str(job.id),
            job_info=job_info,
            task_function=task_function,
        )

        # Add to the database (only once successfully added to APScheduler)
        job = self.db_conn.jobs.create(job)

        # Return the created job
        return Job.model_validate(job)

    def get_jobs(self) -> list[Job]:
        """Returns a list of all Jobs"""

        return TypeAdapter(list[Job]).validate_python(self.db_conn.jobs.get_all())

    def get_job(self, job_id: str) -> Job:
        """Returns a Job given its id"""

        return Job.model_validate(self.db_conn.jobs.get(job_id))

    def delete_job(self, job_id: str) -> None:
        """Deletes a Job

        Args:
            job_id (str): ID of the Job to delete
        """

        self._scheduler.remove_job(job_id)
        self.db_conn.jobs.delete(job_id)
