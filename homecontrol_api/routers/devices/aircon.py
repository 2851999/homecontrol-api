from fastapi import APIRouter, status
from homecontrol_base import exceptions as base_exceptions

from homecontrol_api.devices.aircon.schemas import (
    ACDevice,
    ACDevicePost,
    ACDeviceState,
    ACDeviceStatePut,
)
from homecontrol_api.exceptions import DeviceNotFoundError
from homecontrol_api.routers.dependencies import AdminUser, AnyUser, BaseService

# Currently doesn't work https://github.com/tiangolo/fastapi/discussions/9664
# @asynccontextmanager
# async def lifespan(router: APIRouter):
#     yield

aircon = APIRouter(prefix="/devices/aircon", tags=["aircon"])


@aircon.get(path="", summary="Get a list of all aircon devices")
async def get_devices(user: AnyUser, base_service: BaseService) -> list[ACDevice]:
    return base_service.db_conn.ac_devices.get_all()


@aircon.get(path="/{device_id}")
async def get_device(
    device_id: str, user: AnyUser, base_service: BaseService
) -> ACDevice:
    return base_service.db_conn.ac_devices.get(device_id)


@aircon.post(
    path="",
    summary="Register an air conditioning device",
    status_code=status.HTTP_201_CREATED,
)
async def register_device(
    device_info: ACDevicePost, user: AdminUser, base_service: BaseService
) -> ACDevice:
    try:
        # The AC manager returns the actual device, not the database entry
        return (
            await base_service.aircon.add_device(
                name=device_info.name, ip_address=str(device_info.ip_address)
            )
        ).info
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@aircon.delete(
    path="/{device_id}",
    summary="Delete a registered air conditioning device",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_device(
    device_id: str, user: AdminUser, base_service: BaseService
) -> None:
    try:
        base_service.aircon.remove_device(device_id)
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@aircon.get(path="/{device_id}/state")
async def get_device_state(
    device_id: str, user: AnyUser, base_service: BaseService
) -> ACDeviceState:
    device = await base_service.aircon.get_device(device_id=device_id)
    return await device.get_state()


@aircon.put(path="/{device_id}/state")
async def put_device_state(
    device_id: str, state: ACDeviceStatePut, user: AnyUser, base_service: BaseService
) -> ACDeviceState:
    device = await base_service.aircon.get_device(device_id=device_id)
    await device.set_state(state=state)
    return await device.get_state()
