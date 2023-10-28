import json

from fastapi import APIRouter
from homecontrol_base import exceptions as base_exceptions

from homecontrol_api.devices.aircon.schemas import (
    ACDevice,
    ACDevicePost,
    ACDeviceState,
    ACDeviceStatePost,
)
from homecontrol_api.exceptions import DeviceNotFoundError
from homecontrol_api.routers.dependencies import AdminUser, AnyUser, BaseService

# Currently doesn't work https://github.com/tiangolo/fastapi/discussions/9664
# @asynccontextmanager
# async def lifespan(router: APIRouter):
#     yield

aircon = APIRouter(prefix="/devices/aircon", tags=["aircon"])


@aircon.get(path="/", summary="Get a list of all aircon devices")
async def get_device(user: AnyUser, base_service: BaseService) -> list[ACDevice]:
    return base_service._db_conn.ac_devices.get_all()


@aircon.post(path="/", summary="Register an air conditioning device")
async def register_device(
    device_info: ACDevicePost, user: AdminUser, base_service: BaseService
) -> ACDevice:
    try:
        # The AC manager returns the actual device, not the database entry
        return (
            await base_service.aircon.add_device(
                name=device_info.name, ip_address=str(device_info.ip_address)
            )
        ).get_info()
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@aircon.get(path="/{device_id}/state")
async def get_device_state(
    device_id: str, user: AnyUser, base_service: BaseService
) -> ACDeviceState:
    device = await base_service.aircon.get_device(device_id=device_id)
    return await device.get_state()


@aircon.post(path="/{device_id}/state")
async def post_device_state(
    device_id: str, state: ACDeviceStatePost, user: AnyUser, base_service: BaseService
) -> ACDeviceState:
    device = await base_service.aircon.get_device(device_id=device_id)
    await device.set_state(state=state)
    return await device.get_state()
