from uuid import UUID

from homecontrol_base.database.core import DatabaseConnection
from homecontrol_base.exceptions import DatabaseEntryNotFoundError
from sqlalchemy.orm import Session

from homecontrol_api.database.models import JobInDB


class JobsDBConnection(DatabaseConnection):
    """Handles JobInDB's in the database"""

    def __init__(self, session: Session):
        super().__init__(session)

    def create(self, job: JobInDB) -> JobInDB:
        """Adds a JobInDB to the database

        Args:
            job (JobInDB): Job to add to the database
        """
        self._session.add(job)
        self._session.commit()
        self._session.refresh(job)
        return job

    def get(self, job_id: str) -> JobInDB:
        """Returns JobInDB given a Job's ID

        Args:
            job_id (str): ID of the Job

        Returns:
            JobInDB: The Job

        Raises:
            DatabaseEntryNotFoundError: If the Job isn't found
        """

        job = self._session.query(JobInDB).filter(JobInDB.id == UUID(job_id)).first()
        if not job:
            raise DatabaseEntryNotFoundError(f"job with id '{job_id}' was not found")
        return job

    def get_all(self) -> list[JobInDB]:
        """Returns a list of information about all jobs"""
        return self._session.query(JobInDB).all()

    def count(self) -> int:
        """Returns the number of jobs in the database"""
        return self._session.query(JobInDB).count()

    def update(self, job: JobInDB) -> None:
        """Commits changes that have already been assigned to a Job"""
        self._session.commit()
        self._session.refresh(job)

    def delete(self, job_id: str):
        """Deletes a JobInDB given the Job's id

        Args:
            job_id (str): ID of the Job

        Raises:
            DatabaseEntryNotFoundError: If the Job isn't found
        """
        rows_deleted = (
            self._session.query(JobInDB).filter(JobInDB.id == UUID(job_id)).delete()
        )

        if rows_deleted == 0:
            raise DatabaseEntryNotFoundError(f"Job with id '{job_id}' was not found")

        self._session.commit()
