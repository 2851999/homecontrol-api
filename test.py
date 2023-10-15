from homecontrol_base.database.homecontrol_base.database import database as homecontrol_base_db

from homecontrol_api.database.database import database as homecontrol_api_db

homecontrol_base_db.create_tables()
homecontrol_api_db.create_tables()