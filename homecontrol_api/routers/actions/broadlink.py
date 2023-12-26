from fastapi import APIRouter, status
from homecontrol_base.broadlink import exceptions as broadlink_exceptions

from homecontrol_api.devices.broadlink.schemas import BroadlinkAction
from homecontrol_api.exceptions import ActionNotFoundError
from homecontrol_api.routers.dependencies import AdminUser, AnyUser, BaseService

broadlink_actions = APIRouter(prefix="/actions/broadlink", tags=["broadlink-actions"])


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


@broadlink_actions.delete(path="/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(
    action_id: str, user: AdminUser, base_service: BaseService
) -> None:
    try:
        return base_service.db_conn.broadlink_actions.delete(action_id)
    except broadlink_exceptions.ActionNotFoundError as exc:
        raise ActionNotFoundError(str(exc)) from exc
