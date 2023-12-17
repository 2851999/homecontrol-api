from typing import Generic

from homecontrol_base.database.core import TDatabaseConnection
from homecontrol_base.service.homecontrol_base import HomeControlBaseService


class BaseAPIService(Generic[TDatabaseConnection]):
    """Used for handling a database connection over a longer period of time
    e.g. during a REST API endpoint execution"""

    _db_conn: TDatabaseConnection
    _base_service: HomeControlBaseService

    def __init__(
        self, db_conn: TDatabaseConnection, base_service: HomeControlBaseService
    ) -> None:
        self._db_conn = db_conn
        self._base_service = base_service
