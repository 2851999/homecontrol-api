from homecontrol_base.config.database import DatabaseConfig
from homecontrol_base.database.core import Database, DatabaseConnection

from homecontrol_api.database.models import Base


class HomeControlAPIDatabaseConnection(DatabaseConnection):
    """Class for handling a connection to the homecontrol-api database"""

class HomeControlAPIDatabase(Database[HomeControlAPIDatabaseConnection]):
    """Database for storing information handled by homecontrol-api"""

    def __init__(self, config: DatabaseConfig) -> None:
        super().__init__("homecontrol_api", Base, HomeControlAPIDatabaseConnection, config)

database = HomeControlAPIDatabase(DatabaseConfig())