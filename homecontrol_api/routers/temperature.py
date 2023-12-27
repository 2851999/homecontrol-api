from datetime import datetime
from typing import Optional
from fastapi import APIRouter

from homecontrol_api.routers.dependencies import AnyUser, APIService
from homecontrol_api.temperature.schemas import HistoricTemperature, Temperature

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


@temperature.get("/historic")
async def get_historic_temperatures(
    user: AnyUser,
    api_service: APIService,
    room_name: Optional[str] = None,
    start_timestamp: Optional[datetime] = None,
    end_timestamp: Optional[datetime] = None,
) -> list[HistoricTemperature]:
    return api_service.db_conn.temperatures.get_all(
        room_name=room_name,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )
