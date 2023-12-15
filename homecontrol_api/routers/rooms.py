from fastapi import APIRouter, status

from homecontrol_api.rooms.schemas import Room, RoomPost
from homecontrol_api.routers.dependencies import AdminUser, AnyUser, APIService

rooms = APIRouter(prefix="/rooms", tags=["rooms"])


@rooms.get("/")
async def get_rooms(user: AnyUser, api_service: APIService) -> list[Room]:
    return api_service.room.get_rooms()


@rooms.post("/")
async def create_room(
    room_info: RoomPost, user: AdminUser, api_service: APIService
) -> Room:
    return api_service.room.create_room(room_info)


@rooms.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: str, user: AdminUser, api_service: APIService) -> None:
    return api_service.room.delete_room(room_id)
