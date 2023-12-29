from typing import Optional

from fastapi import APIRouter, status

from homecontrol_api.actions.schemas import RoomAction, RoomActionPost
from homecontrol_api.core.types import UUIDString
from homecontrol_api.routers.dependencies import AdminUser, AnyUser, APIService

room_actions = APIRouter(prefix="/actions/room", tags=["room-actions"])


@room_actions.post(path="")
async def create_action(
    action_info: RoomActionPost, user: AdminUser, api_service: APIService
) -> RoomAction:
    return await api_service.action.create_room_action(action_info=action_info)


@room_actions.get(path="")
async def get_actions(
    user: AnyUser, api_service: APIService, room_id: Optional[UUIDString] = None
) -> list[RoomAction]:
    return api_service.db_conn.room_actions.get_all(room_id=room_id)


@room_actions.post(path="/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def execute_action(
    action_id: str, user: AnyUser, api_service: APIService
) -> None:
    await api_service.action.execute_room_action(action_id=action_id)
