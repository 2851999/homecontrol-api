from homecontrol_base.service.homecontrol_base import HomeControlBaseService

from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.rooms.schemas import ControlType
from homecontrol_api.rooms.service import RoomService
from homecontrol_api.service.core import BaseAPIService
from homecontrol_api.temperature.schemas import Temperature


class TemperatureService(BaseAPIService[HomeControlAPIDatabaseConnection]):
    """Service for handling temperatures"""

    def __init__(
        self,
        db_conn: HomeControlAPIDatabaseConnection,
        base_service: HomeControlBaseService,
        room_service: RoomService,
    ) -> None:
        super().__init__(db_conn, base_service)

        self._room_service = room_service

    async def get_outdoor_temperature(self) -> Temperature:
        """Obtains the outdoor temperature (Based on the first available AC unit)"""
        ac_device_infos = self._base_service._db_conn.ac_devices.get_all()
        if len(ac_device_infos) == 0:
            return Temperature(value=None)
        ac_device = await self._base_service.aircon.get_device(
            str(ac_device_infos[0].id)
        )
        ac_state = await ac_device.get_state()
        return Temperature(value=ac_state.outdoor_temperature)

    async def get_room_temperature(self, room_id: str) -> Temperature:
        """Returns the temperature of a Room (based on available AC units)"""

        # Obtain the room
        room = self._room_service.get_room(room_id=room_id)

        # Find any AC device
        ac_device_id = None
        for controller in room.controllers:
            if controller.control_type == ControlType.AC:
                ac_device_id = controller.id
                break

        # Fetch the value
        if ac_device_id is None:
            return Temperature(value=None)

        ac_device = await self._base_service.aircon.get_device(ac_device_id)
        ac_state = await ac_device.get_state()
        return Temperature(value=ac_state.indoor_temperature)
