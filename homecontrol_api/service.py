
from contextlib import contextmanager
from typing import Optional

from homecontrol_base.service.core import BaseService

from homecontrol_api.database.database import HomeControlAPIDatabaseConnection
from homecontrol_api.database.database import database as homecontrol_api_db
from homecontrol_api.users.service import UserService


class HomeControlAPIService(BaseService[HomeControlAPIDatabaseConnection]):
    """Service for homecontrol_api"""

    _user: Optional[UserService] = None

    def __init__(self, db_conn: HomeControlAPIDatabaseConnection) -> None:
        super().__init__(db_conn)

    # Below are properties that create the sub services when required
    
    @property
    def user(self) -> UserService:
        if not self._user:
            self._user = UserService(self._db_conn)
        return self._user
    
@contextmanager
def create_homecontrol_api_service():
    """Creates an instance of HomeControlAPIService"""
    with homecontrol_api_db.connect() as conn:
        yield HomeControlAPIService(conn)
