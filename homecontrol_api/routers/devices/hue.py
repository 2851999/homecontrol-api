from typing import Optional

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from homecontrol_base.hue import exceptions as hue_exceptions
from homecontrol_base.hue import structs as hue_structs

from homecontrol_api.devices.hue.schemas import (
    HueBridge,
    HueBridgeDiscoverInfo,
    HueBridgePost,
)
from homecontrol_api.routers.dependencies import AdminUser, AnyUser, BaseService

hue = APIRouter(prefix="/devices/hue", tags=["hue"])


@hue.get(path="/discover", summary="Get a list of all hue bridges found on the network")
async def discover_bridges(
    user: AdminUser, base_service: BaseService
) -> list[HueBridgeDiscoverInfo]:
    return base_service.hue.discover()


@hue.get(path="", summary="Get a list of all registered  hue bridges")
async def get_devices(user: AnyUser, base_service: BaseService) -> list[HueBridge]:
    return base_service._db_conn.hue_bridges.get_all()


@hue.post(path="", summary="Register a hue bridge", status_code=status.HTTP_201_CREATED)
async def register_device(
    device_info: HueBridgePost, user: AdminUser, base_service: BaseService
) -> Optional[HueBridge]:
    try:
        # The hue manager returns the actual hue bridge, not the database entry
        return base_service.hue.add_bridge(
            name=device_info.name,
            discover_info=hue_structs.HueBridgeDiscoverInfo(
                **device_info.discover_info.model_dump()
            ),
        ).info
    except hue_exceptions.HueBridgeButtonNotPressedError:
        # Status OK but not created
        return JSONResponse(
            content={"detail": "Button on the bridge should now be pressed"},
            status_code=200,
        )
