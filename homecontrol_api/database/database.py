from typing import Optional

from homecontrol_base.config.database import DatabaseConfig
from homecontrol_base.database.core import Database, DatabaseConnection
from sqlalchemy.orm import Session

from homecontrol_api import migrations
from homecontrol_api.database.jobs import JobsDBConnection
from homecontrol_api.database.models import Base
from homecontrol_api.database.room_actions import RoomActionsDBConnection
from homecontrol_api.database.rooms import RoomsDBConnection
from homecontrol_api.database.temperatures import TemperaturesDBConnection
from homecontrol_api.database.user_sessions import UserSessionsDBConnection
from homecontrol_api.database.users import UsersDBConnection


class HomeControlAPIDatabaseConnection(DatabaseConnection):
    """Class for handling a connection to the homecontrol-api database"""

    _users: Optional[UsersDBConnection] = None
    _user_sessions: Optional[UserSessionsDBConnection] = None
    _rooms: Optional[RoomsDBConnection] = None
    _temperatures: Optional[TemperaturesDBConnection] = None
    _jobs: Optional[JobsDBConnection] = None
    _room_actions: Optional[RoomActionsDBConnection] = None

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

    @property
    def temperatures(self) -> TemperaturesDBConnection:
        """Returns a TemperaturesDBConnection while caching it"""
        if not self._temperatures:
            self._temperatures = TemperaturesDBConnection(self._session)
        return self._temperatures

    @property
    def jobs(self) -> JobsDBConnection:
        """Returns a JobsDBConnection while caching it"""
        if not self._jobs:
            self._jobs = JobsDBConnection(self._session)
        return self._jobs

    @property
    def room_actions(self) -> RoomActionsDBConnection:
        """Returns a RoomActionsDBConnection while caching it"""
        if not self._room_actions:
            self._room_actions = RoomActionsDBConnection(self._session)
        return self._room_actions


class HomeControlAPIDatabase(Database[HomeControlAPIDatabaseConnection]):
    """Database for storing information handled by homecontrol-api"""

    def __init__(self, config: DatabaseConfig) -> None:
        super().__init__(
            "homecontrol_api",
            Base,
            HomeControlAPIDatabaseConnection,
            config,
        )


database = HomeControlAPIDatabase(DatabaseConfig())
