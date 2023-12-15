from typing import Optional

from homecontrol_base.config.database import DatabaseConfig
from homecontrol_base.database.core import Database, DatabaseConnection
from sqlalchemy.orm import Session

from homecontrol_api.database.models import Base
from homecontrol_api.database.rooms import RoomsDBConnection
from homecontrol_api.database.user_sessions import UserSessionsDBConnection
from homecontrol_api.database.users import UsersDBConnection


class HomeControlAPIDatabaseConnection(DatabaseConnection):
    """Class for handling a connection to the homecontrol-api database"""

    _users: Optional[UsersDBConnection] = None
    _user_sessions: Optional[UserSessionsDBConnection] = None
    _rooms: Optional[RoomsDBConnection] = None

    def __init__(self, session: Session):
        super().__init__(session)

    @property
    def users(self) -> UsersDBConnection:
        """Returns a UsersDBConnection while caching it"""
        if not self._users:
            self._users = UsersDBConnection(self._session)
        return self._users

    @property
    def user_sessions(self) -> UserSessionsDBConnection:
        """Returns a UserSessionsDBConnection while caching it"""
        if not self._user_sessions:
            self._user_sessions = UserSessionsDBConnection(self._session)
        return self._user_sessions

    @property
    def rooms(self) -> RoomsDBConnection:
        """Returns a RoomsDBConnection while caching it"""
        if not self._rooms:
            self._rooms = RoomsDBConnection(self._session)
        return self._rooms


class HomeControlAPIDatabase(Database[HomeControlAPIDatabaseConnection]):
    """Database for storing information handled by homecontrol-api"""

    def __init__(self, config: DatabaseConfig) -> None:
        super().__init__(
            "homecontrol_api", Base, HomeControlAPIDatabaseConnection, config
        )


database = HomeControlAPIDatabase(DatabaseConfig())
