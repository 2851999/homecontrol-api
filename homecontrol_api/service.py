from contextlib import contextmanager
from typing import Generator, Optional

from homecontrol_base.service.core import BaseService

from homecontrol_api.authentication.service import AuthService
from homecontrol_api.config.api import APIConfig
from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.database import database as homecontrol_api_db
from homecontrol_api.rooms.service import RoomService


class HomeControlAPIService(BaseService[HomeControlAPIDatabaseConnection]):
    """Service for homecontrol_api"""

    _api_config: APIConfig
    _auth: Optional[AuthService] = None
    _room: Optional[RoomService] = None

    def __init__(self, db_conn: HomeControlAPIDatabaseConnection) -> None:
        super().__init__(db_conn)

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
        """Returns an RoomService while caching it"""
        if not self._room:
            self._room = RoomService(self._db_conn)
        return self._room


@contextmanager
def create_homecontrol_api_service() -> Generator[HomeControlAPIService, None, None]:
    """Creates an instance of HomeControlAPIService (for use in scripts)"""
    with homecontrol_api_db.connect() as conn:
        yield HomeControlAPIService(conn)


def get_homecontrol_api_service() -> HomeControlAPIService:
    """Creates an instance of HomeControlAPIService (for use in FastAPI)"""
    with homecontrol_api_db.connect() as conn:
        yield HomeControlAPIService(conn)
