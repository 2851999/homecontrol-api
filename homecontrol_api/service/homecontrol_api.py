from contextlib import contextmanager
from typing import Generator, Optional

from homecontrol_base.service.homecontrol_base import (
    HomeControlBaseService,
    create_homecontrol_base_service,
)
from homecontrol_api.actions.service import ActionService

from homecontrol_api.authentication.service import AuthService
from homecontrol_api.config.api import APIConfig
from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.database import database as homecontrol_api_db
from homecontrol_api.rooms.service import RoomService
from homecontrol_api.scheduler.core import Scheduler
from homecontrol_api.scheduler.service import SchedulerService
from homecontrol_api.service.core import BaseAPIService
from homecontrol_api.temperature.service import TemperatureService


class HomeControlAPIService(BaseAPIService[HomeControlAPIDatabaseConnection]):
    """Service for homecontrol_api"""

    _api_config: APIConfig
    _scheduler: Scheduler
    _auth: Optional[AuthService] = None
    _room: Optional[RoomService] = None
    _temperature: Optional[TemperatureService] = None
    _scheduler_service: Optional[SchedulerService] = None
    _action: Optional[ActionService] = None

    def __init__(
        self,
        db_conn: HomeControlAPIDatabaseConnection,
        base_service: HomeControlBaseService,
        scheduler: Optional[Scheduler],
    ) -> None:
        """When the scheduler is None will automatically create only if needed"""
        super().__init__(db_conn, base_service)

        self._api_config = APIConfig()
        self._scheduler = scheduler

    # Below are properties that create the sub services when required

    @property
    def auth(self) -> AuthService:
        """Returns an AuthService while caching it"""
        if not self._auth:
            self._auth = AuthService(self.db_conn, self._api_config)
        return self._auth

    @property
    def room(self) -> RoomService:
        """Returns a RoomService while caching it"""
        if not self._room:
            self._room = RoomService(self.db_conn)
        return self._room

    @property
    def temperature(self) -> TemperatureService:
        """Returns a TemperatureService while caching it"""
        if not self._temperature:
            self._temperature = TemperatureService(
                self.db_conn, self.base_service, self.room
            )
        return self._temperature

    @property
    def scheduler(self) -> SchedulerService:
        """Returns a TemperatureService while caching it"""
        if not self._scheduler_service:
            if self._scheduler is None:
                self._scheduler = Scheduler()
            self._scheduler_service = SchedulerService(self.db_conn, self._scheduler)
        return self._scheduler_service

    @property
    def action(self) -> ActionService:
        """Returns a ActionService while caching it"""
        if not self._action:
            self._action = ActionService(self.db_conn, self.base_service)
        return self._action


@contextmanager
def create_homecontrol_api_service(
    base_service: Optional[HomeControlBaseService] = None,
    scheduler: Optional[Scheduler] = None,
) -> Generator[HomeControlAPIService, None, None]:
    """Creates an instance of HomeControlAPIService (for use in scripts)"""
    with homecontrol_api_db.connect() as conn:
        if base_service:
            yield HomeControlAPIService(conn, base_service, scheduler)
        else:
            with create_homecontrol_base_service() as new_base_service:
                yield HomeControlAPIService(conn, new_base_service, scheduler)
