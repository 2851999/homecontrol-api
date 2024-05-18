import uuid
from homecontrol_base.service.core import BaseService
from pydantic import TypeAdapter

from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.models import JobInDB
from homecontrol_api.scheduler.core import Scheduler
from homecontrol_api.scheduler.schemas import Job, JobPatch, JobPost, JobStatus
from homecontrol_api.scheduler.tasks import task_handler


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
        """

        # Create the database model (and ensure id is created before adding)
        job = JobInDB(**job_info.model_dump(), id=uuid.uuid4(), status=JobStatus.ACTIVE)

        # Add to the scheduler
        self._scheduler.add_job(
            job_id=str(job.id),
            job_info=job_info,
            task_function=task_handler,
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

    def update_job(self, job_id: str, job_data: JobPatch) -> Job:
        """Updates a job

        Args:
            job_id (str): ID of the Job to update
            job_data (JobPatch): Data to update in the Job
        """

        # Obtain the Job
        job = self.db_conn.jobs.get(job_id)

        # Check if status changing and update the job in the scheduler if necessary
        if job_data.status is not None and job_data.status != job.status:
            if job_data.status == JobStatus.ACTIVE:
                self._scheduler.resume_job(job_id=job_id)
            elif job_data.status == JobStatus.PAUSED:
                self._scheduler.pause_job(job_id=job_id)

        # Check if task itself changing
        update_trigger: bool = job_data.trigger is not None

        if update_trigger:
            new_trigger = None
            if update_trigger:
                new_trigger = job_data.trigger

            self._scheduler.modify_job(
                job_id=job_id,
                new_trigger=new_trigger,
            )

        # Assign the new data
        update_data = job_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(job, key, value)

        # Update and return the updated data
        self.db_conn.jobs.update(job)
        return Job.model_validate(job)

    def delete_job(self, job_id: str) -> None:
        """Deletes a Job

        Args:
            job_id (str): ID of the Job to delete
        """

        self._scheduler.remove_job(job_id)
        self.db_conn.jobs.delete(job_id)
