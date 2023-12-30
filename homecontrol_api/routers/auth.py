from fastapi import APIRouter, Response, status

from homecontrol_api.authentication.schemas import (
    LoginPost,
    User,
    UserAccountType,
    UserPatch,
    UserPost,
    UserSession,
)
from homecontrol_api.exceptions import InsufficientCredentialsError
from homecontrol_api.routers.dependencies import (
    AdminUser,
    AnySession,
    AnyUser,
    APIService,
    RefreshToken,
)

auth = APIRouter(prefix="/auth", tags=["auth"])


@auth.get("/user", summary="Check authentication")
async def get_user(user: AnyUser) -> User:
    return user


@auth.post("/user", summary="Create user", status_code=status.HTTP_201_CREATED)
async def create_user(user_info: UserPost, api_service: APIService) -> User:
    return api_service.auth.create_user(user_info=user_info)


@auth.patch("/user/{user_id}")
async def patch_user(
    user_id: str, user_data: UserPatch, user: AdminUser, api_service: APIService
) -> User:
    return api_service.auth.update_user(user_id=user_id, user_data=user_data)


@auth.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, user: AnyUser, api_service: APIService):
    # Only allow an admin to delete users that are not themselves
    if user.id != user_id and user.account_type != UserAccountType.ADMIN:
        raise InsufficientCredentialsError("Insufficient credentials")
    return api_service.auth.delete_user(user_id)


@auth.get("/users", summary="Obtain a list of all users")
async def get_users(user: AdminUser, api_service: APIService) -> list[User]:
    return api_service.auth.db_conn.users.get_all()


@auth.post("/login", summary="Login as a user")
async def login(
    login_info: LoginPost, response: Response, api_service: APIService
) -> UserSession:
    return api_service.auth.login(login_info=login_info, response=response)


@auth.post("/refresh", summary="Refresh a user session")
async def refresh(
    refresh_token: RefreshToken, response: Response, api_service: APIService
) -> UserSession:
    return api_service.auth.refresh_user_session(
        refresh_token=refresh_token, response=response
    )


@auth.post(
    "/logout",
    summary="Logout and invalidate the user session",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    current_session: AnySession, response: Response, api_service: APIService
) -> None:
    api_service.auth.logout(user_session_id=current_session.id, response=response)
