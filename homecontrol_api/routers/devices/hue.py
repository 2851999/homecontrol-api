from typing import Optional

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from homecontrol_base import exceptions as base_exceptions
from homecontrol_base.hue import exceptions as hue_exceptions
from homecontrol_base.hue import structs as hue_structs

from homecontrol_api.devices.hue.schemas import (
    HueBridge,
    HueBridgeDiscoverInfo,
    HueBridgePost,
)
from homecontrol_api.exceptions import DeviceNotFoundError, TooManyRequestsError
from homecontrol_api.routers.dependencies import AdminUser, AnyUser, BaseService

hue = APIRouter(prefix="/devices/hue", tags=["hue"])


@hue.get(path="/discover", summary="Get a list of all hue bridges found on the network")
async def discover_bridges(
    user: AdminUser, base_service: BaseService
) -> list[HueBridgeDiscoverInfo]:
    try:
        return base_service.hue.discover()
    except hue_exceptions.HueBridgesDiscoveryError as exc:
        raise TooManyRequestsError(
            "Too many requests, try using mDNS for Hue Bridge discovery instead"
        ) from exc

    # HACKY WAY TO TEST IN DEVELOPMENT - JUST SEND BACK KNOWN (mDNS discovery does not work using
    # Docker for Windows/WSL - causing rate limit issues with the meethue site)
    # bridges = base_service.db_conn.hue_bridges.get_all()
    # return [
    #     HueBridgeDiscoverInfo(
    #         id=bridge.identifier, internalipaddress=bridge.ip_address, port=bridge.port
    #     )
    #     for bridge in bridges
    # ]


@hue.get(path="", summary="Get a list of all registered  hue bridges")
async def get_bridges(user: AnyUser, base_service: BaseService) -> list[HueBridge]:
    return base_service.db_conn.hue_bridges.get_all()


@hue.get(path="/{bridge_id}")
async def get_bridge(bridge_id: str, base_service: BaseService) -> HueBridge:
    return base_service.db_conn.hue_bridges.get(bridge_id)


@hue.post(path="", summary="Register a hue bridge", status_code=status.HTTP_201_CREATED)
async def register_bridge(
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


@hue.delete(
    path="/{bridge_id}",
    summary="Delete a registered Hue bridge",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_bridge(
    bridge_id: str, user: AdminUser, base_service: BaseService
) -> None:
    try:
        base_service.hue.remove_bridge(bridge_id)
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@hue.get(path="/{bridge_id}/rooms")
async def get_rooms(
    bridge_id: str, user: AnyUser, base_service: BaseService
) -> list[hue_structs.HueRoom]:
    try:
        with base_service.hue.get_bridge(bridge_id).connect() as conn:
            return conn.get_rooms()
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@hue.get(path="/{bridge_id}/rooms/{room_id}")
async def get_room(
    bridge_id: str, room_id: str, user: AnyUser, base_service: BaseService
) -> hue_structs.HueRoom:
    try:
        with base_service.hue.get_bridge(bridge_id).connect() as conn:
            return conn.get_room(room_id)
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@hue.get(path="/{bridge_id}/rooms/{room_id}/state")
async def get_room_state(
    bridge_id: str, room_id: str, user: AnyUser, base_service: BaseService
):
    try:
        with base_service.hue.get_bridge(bridge_id).connect() as conn:
            return conn.get_room_state(room_id)
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc


@hue.patch(path="/{bridge_id}/rooms/{room_id}/state")
async def set_room_state(
    bridge_id: str,
    room_id: str,
    update_data: hue_structs.HueRoomStateUpdate,
    user: AnyUser,
    base_service: BaseService,
):
    try:
        with base_service.hue.get_bridge(bridge_id).connect() as conn:
            return conn.set_room_state(room_id=room_id, update_data=update_data)
    except base_exceptions.DeviceNotFoundError as exc:
        raise DeviceNotFoundError(str(exc)) from exc
