from contextlib import contextmanager
from typing import Generator, Optional

from homecontrol_base.service.homecontrol_base import (
    HomeControlBaseService,
    create_homecontrol_base_service,
)

from homecontrol_api.authentication.service import AuthService
from homecontrol_api.config.api import APIConfig
from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.database import database as homecontrol_api_db
from homecontrol_api.rooms.service import RoomService
from homecontrol_api.service.core import BaseAPIService
from homecontrol_api.temperature.service import TemperatureService


class HomeControlAPIService(BaseAPIService[HomeControlAPIDatabaseConnection]):
    """Service for homecontrol_api"""

    _api_config: APIConfig
    _auth: Optional[AuthService] = None
    _room: Optional[RoomService] = None
    _temperature: Optional[TemperatureService] = None

    def __init__(
        self,
        db_conn: HomeControlAPIDatabaseConnection,
        base_service: HomeControlBaseService,
    ) -> None:
        super().__init__(db_conn, base_service)

        self._api_config = APIConfig()

    # Below are properties that create the sub services when required

    @property
    def auth(self) -> AuthService:
        """Returns an AuthService while caching it"""
        if not self._auth:
            self._auth = AuthService(self._db_conn, self._api_config)
        return self._auth

    @property
    def room(self) -> RoomService:
        """Returns a RoomService while caching it"""
        if not self._room:
            self._room = RoomService(self._db_conn)
        return self._room

    @property
    def temperature(self) -> TemperatureService:
        """Returns a TemperatureService while caching it"""
        if not self._room:
            self._room = TemperatureService(
                self._db_conn, self._base_service, self.room
            )
        return self._room


@contextmanager
def create_homecontrol_api_service(
    base_service: Optional[HomeControlBaseService] = None,
) -> Generator[HomeControlAPIService, None, None]:
    """Creates an instance of HomeControlAPIService (for use in scripts)"""
    with homecontrol_api_db.connect() as conn:
        if base_service:
            yield HomeControlAPIService(conn, base_service)
        else:
            with create_homecontrol_base_service() as new_base_service:
                yield HomeControlAPIService(conn, new_base_service)
