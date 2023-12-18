from fastapi import APIRouter

from homecontrol_api.routers.dependencies import AnyUser, APIService
from homecontrol_api.temperature.schemas import Temperature

temperature = APIRouter(prefix="/temperature", tags=["temperature"])


@temperature.get("/outdoor")
async def get_outdoor_temperature(
    user: AnyUser, api_service: APIService
) -> Temperature:
    return await api_service.temperature.get_outdoor_temperature()


@temperature.get("/room/{room_id}")
async def get_room_temperature(
    room_id: str, user: AnyUser, api_service: APIService
) -> Temperature:
    return await api_service.temperature.get_room_temperature(room_id)
