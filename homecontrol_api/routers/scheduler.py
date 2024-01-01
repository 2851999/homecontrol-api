from fastapi import APIRouter, status

from homecontrol_api.routers.dependencies import AdminUser, APIService
from homecontrol_api.scheduler.schemas import Job, JobPatch, JobPost
from homecontrol_api.scheduler.tasks import AVAILABLE_TASKS

scheduler = APIRouter(prefix="/scheduler", tags=["scheduler"])


@scheduler.get("/available_tasks")
async def get_available_tasks(user: AdminUser, api_service: APIService) -> list[str]:
    return AVAILABLE_TASKS.keys()


@scheduler.get("/jobs")
async def get_jobs(user: AdminUser, api_service: APIService) -> list[Job]:
    return api_service.scheduler.get_jobs()


@scheduler.post("/jobs")
async def create_job(
    job_info: JobPost, user: AdminUser, api_service: APIService
) -> Job:
    return api_service.scheduler.create_job(job_info)


@scheduler.patch("/jobs/{job_id}")
async def patch_job(
    job_id: str, job_data: JobPatch, user: AdminUser, api_service: APIService
) -> Job:
    return api_service.scheduler.update_job(job_id=job_id, job_data=job_data)


@scheduler.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, user: AdminUser, api_service: APIService) -> None:
    return api_service.scheduler.delete_job(job_id)
