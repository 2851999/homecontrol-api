from homecontrol_base.database.homecontrol_base.database import (
    database as homecontrol_base_db,
)

from homecontrol_api.database.database import database as homecontrol_api_db
from homecontrol_api.schemas import LoginPost, UserAccountType, UserPost
from homecontrol_api.service import create_homecontrol_api_service

homecontrol_base_db.create_tables()
homecontrol_api_db.create_tables()

with create_homecontrol_api_service() as service:
    # user = service.user.create_user(
    #     UserPost(username="Me", password="test", account_type=UserAccountType.ADMIN)
    # )
    # print(service.user.get_user(user.id))

    session = service.user.authenticate_user(LoginPost(username="Me", password="test"))
    print(session)
