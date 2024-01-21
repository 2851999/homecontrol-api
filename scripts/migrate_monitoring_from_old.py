"""
Migrates monitoring data from homecontrol-old to homecontrol-api

Should be able to just update ROOM_NAMES, and the local database config to point to
database and then run
"""
import sqlite3
from datetime import datetime
from typing import List

from homecontrol_api.database.database import database as new_database
from homecontrol_api.database.models import TemperatureInDB

# Names of the Rooms from the old version and their new counterpart
ROOM_NAMES = [
    ("Games_Room", "Games Room"),
    ("Joel_s_Room", "Joel's Room"),
    ("Spare Room", "Spare Room"),
    ("Mum_s_Room", "Mum's Room"),
    ("outdoor", "outdoor"),
]

# Old data path
OLD_DATA_PATH = "test-old-temps/"


class OldDatabaseConnection:
    """
    Handles a connection to a sqlite3 database (From homecontrol-old)
    """

    # Path of this database
    path: str

    # Connection
    _conn: sqlite3.Connection
    _cursor: sqlite3.Cursor

    def __init__(self, path: str):
        self.path = path

    def __enter__(self):
        self._conn = sqlite3.connect(self.path)
        self._cursor = self._conn.cursor()

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._conn.close()

    def select_values(
        self,
        table: str,
        values: List[str],
    ):
        """
        Returns values from a table
        """
        sql = f"SELECT {','.join(values)} FROM {table}"
        params = ()

        self._cursor.execute(sql, params)
        return self._cursor.fetchall()

    def commit(self):
        """
        Commits changes
        """
        self._conn.commit()


# Go through each room
for room_names in ROOM_NAMES:
    # Fetch all old data
    data = []
    with OldDatabaseConnection(f"{OLD_DATA_PATH}homecontrol.db") as old_conn:
        data = old_conn.select_values(f"{room_names[0]}_temps", ["timestamp", "temp"])

    # Now need to insert into new database
    with new_database.connect() as new_conn:
        for singleTempData in data:
            new_conn.temperatures.create(
                TemperatureInDB(
                    timestamp=datetime.strptime(singleTempData[0], "%Y-%m-%d %H:%M:%S"),
                    value=singleTempData[1],
                    room_name=room_names[1],
                )
            )
