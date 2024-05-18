from homecontrol_api.scheduler.schemas import (
    TaskExecuteRoomAction,
    TaskRecordAllTemperatures,
)


async def task_handler(job_id: str):
    from homecontrol_api.service.homecontrol_api import create_homecontrol_api_service

    with create_homecontrol_api_service() as service:
        # Obtain the task that needs to be executed
        task = service.scheduler.get_job(job_id).task

        # Execute the task
        if isinstance(task, TaskRecordAllTemperatures):
            await service.temperature.record_all_temperatures_to_db()
        elif isinstance(task, TaskExecuteRoomAction):
            await service.action.execute_room_action(task.action_id)
