from datetime import datetime
from typing import Optional
from homecontrol_base.database.core import DatabaseConnection
from sqlalchemy.orm import Session

from homecontrol_api.database.models import TemperatureInDB


class TemperaturesDBConnection(DatabaseConnection):
    """Handles TemperatureInDB's in the database"""

    def __init__(self, session: Session):
        super().__init__(session)

    def create(self, temperature: TemperatureInDB) -> TemperatureInDB:
        """Adds a TemperatureInDB to the database

        Args:
            temperature (TemperatureInDB): Temperature to add to the database
        """

        self._session.add(temperature)
        self._session.commit()
        self._session.refresh(temperature)
        return temperature

    def get_all(
        self,
        room_name: Optional[str] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
    ) -> list[TemperatureInDB]:
        """Returns a list of temperatures with several optional query params"""
        filters = []
        if room_name is not None:
            filters.append(TemperatureInDB.room_name == room_name)
        if start_timestamp is not None:
            filters.append(TemperatureInDB.timestamp >= start_timestamp)
        if end_timestamp is not None:
            filters.append(TemperatureInDB.timestamp < end_timestamp)

        if len(filters) == 0:
            return (
                self._session.query(TemperatureInDB)
                .order_by(TemperatureInDB.timestamp)
                .all()
            )
        else:
            return (
                self._session.query(TemperatureInDB)
                .order_by(TemperatureInDB.timestamp)
                .filter(*filters)
                .all()
            )
