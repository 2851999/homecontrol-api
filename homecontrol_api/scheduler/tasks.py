from typing import Any


async def record_all_temperatures():
    from homecontrol_api.service.homecontrol_api import create_homecontrol_api_service

    with create_homecontrol_api_service() as service:
        await service.temperature.record_all_temperatures_to_db()


AVAILABLE_TASKS: dict[str, Any] = {"record_all_temperatures": record_all_temperatures}
