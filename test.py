from time import sleep
from homecontrol_base.database.homecontrol_base.database import (
    database as homecontrol_base_db,
)

from homecontrol_api.database.database import database as homecontrol_api_db
from homecontrol_api.authentication.schemas import LoginPost, UserAccountType, UserPost
from homecontrol_api.service import create_homecontrol_api_service

homecontrol_base_db.create_tables()
homecontrol_api_db.create_tables()

with create_homecontrol_api_service() as service:
    # user = service.user.create_user(
    #     UserPost(username="Me", password="test", account_type=UserAccountType.ADMIN)
    # )
    # print(service.user.get_user(user.id))

    session = service.user.login(LoginPost(username="Me", password="test"))
    print(str(session.refresh_token))
    # print(session)

    sleep(2)

    user = service.user.authenticate_user(access_token=session.access_token)
    # print(user)
    new_session = service.user.refresh_user_session(refresh_token=session.refresh_token)
    # print(new_session)

    print(str(session.refresh_token))
    print(str(new_session.refresh_token))
    print(str(service.user._db_conn.user_sessions.get(str(session.id)).refresh_token))
