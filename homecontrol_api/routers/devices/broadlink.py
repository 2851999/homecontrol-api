from fastapi import APIRouter, status
from homecontrol_base import exceptions as base_exceptions

from homecontrol_api.devices.broadlink.schemas import (
    BroadlinkAction,
    BroadlinkDevice,
    BroadlinkDevicePlaybackPost,
    BroadlinkDevicePost,
    BroadlinkDeviceRecordPost,
)
from homecontrol_api.exceptions import DeviceNotFoundError
from homecontrol_api.routers.dependencies import AdminUser, AnyUser, BaseService

broadlink = APIRouter(prefix="/devices/broadlink", tags=["broadlink"])


@broadlink.get(path="", summary="Get a list of all broadlink devices")
async def get_devices(
    user: AnyUser, base_service: BaseService
) -> list[BroadlinkDevice]:
    return base_service.db_conn.broadlink_devices.get_all()


@broadlink.get(path="/{device_id}")
async def get_device(
    device_id: str, user: AnyUser, base_service: BaseService
) -> BroadlinkDevice:
    return base_service.db_conn.broadlink_devices.get(device_id)


@broadlink.post(
    path="", summary="Register a broadlink device", status_code=status.HTTP_201_CREATED
)
async def register_device(
    device_info: BroadlinkDevicePost, user: AdminUser, base_service: BaseService
) -> BroadlinkDevice:
    try:
        # The Broadlink manager returns the actual device, not the database entry
        return base_service.broadlink.add_device(
            name=device_info.name, ip_address=str(device_info.ip_address)
        ).info
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@broadlink.delete(
    path="/{device_id}",
    summary="Delete a registered broadlink device",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_device(
    device_id: str, user: AdminUser, base_service: BaseService
) -> None:
    try:
        base_service.broadlink.remove_device(device_id)
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@broadlink.post(path="/{device_id}/record")
async def record_action(
    device_id: str,
    action_info: BroadlinkDeviceRecordPost,
    user: AdminUser,
    base_service: BaseService,
) -> BroadlinkAction:
    try:
        return base_service.broadlink.record_action(
            device_id=device_id, name=action_info.name
        )
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@broadlink.post(path="/{device_id}/playback", status_code=status.HTTP_204_NO_CONTENT)
async def playback_action(
    device_id: str,
    playback_info: BroadlinkDevicePlaybackPost,
    user: AnyUser,
    base_service: BaseService,
) -> None:
    try:
        base_service.broadlink.play_action(
            device_id=device_id, action_id=playback_info.action_id
        )
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc
