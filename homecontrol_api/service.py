from contextlib import contextmanager
from typing import Optional

from homecontrol_base.service.core import BaseService

from homecontrol_api.authentication.service import AuthService
from homecontrol_api.config.api import APIConfig
from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.database import database as homecontrol_api_db


class HomeControlAPIService(BaseService[HomeControlAPIDatabaseConnection]):
    """Service for homecontrol_api"""

    _api_config: APIConfig
    _auth: Optional[AuthService] = None

    def __init__(self, db_conn: HomeControlAPIDatabaseConnection) -> None:
        super().__init__(db_conn)

        self._api_config = APIConfig()

    # Below are properties that create the sub services when required

    @property
    def auth(self) -> AuthService:
        if not self._auth:
            self._auth = AuthService(self._db_conn, self._api_config)
        return self._auth


@contextmanager
def create_homecontrol_api_service() -> HomeControlAPIService:
    """Creates an instance of HomeControlAPIService"""
    with homecontrol_api_db.connect() as conn:
        yield HomeControlAPIService(conn)
