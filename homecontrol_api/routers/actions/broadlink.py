from fastapi import APIRouter, status
from homecontrol_base import exceptions as base_exceptions
from homecontrol_base.broadlink import exceptions as broadlink_exceptions

from homecontrol_api.devices.broadlink.schemas import (
    BroadlinkAction,
    BroadlinkActionPost,
)
from homecontrol_api.exceptions import ActionNotFoundError, DeviceNotFoundError
from homecontrol_api.routers.dependencies import AdminUser, AnyUser, BaseService

broadlink_actions = APIRouter(prefix="/broadlink")


@broadlink_actions.get(path="")
async def get_actions(
    user: AnyUser, base_service: BaseService
) -> list[BroadlinkAction]:
    return base_service.db_conn.broadlink_actions.get_all()


@broadlink_actions.get(path="/{action_id}")
async def get_action(
    action_id: str, user: AnyUser, base_service: BaseService
) -> BroadlinkAction:
    return base_service.db_conn.broadlink_actions.get(action_id=action_id)


@broadlink_actions.post(path="")
async def register_action(
    action_info: BroadlinkActionPost,
    user: AdminUser,
    base_service: BaseService,
) -> BroadlinkAction:
    try:
        return base_service.broadlink.record_action(
            device_id=action_info.device_id, name=action_info.name
        )
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@broadlink_actions.delete(path="/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(
    action_id: str, user: AdminUser, base_service: BaseService
) -> None:
    try:
        return base_service.db_conn.broadlink_actions.delete(action_id)
    except broadlink_exceptions.ActionNotFoundError as exc:
        raise ActionNotFoundError(str(exc)) from exc
