from typing import Annotated

from fastapi import APIRouter, Depends, Header, status

from homecontrol_api.authentication.schemas import (
    LoginPost,
    RefreshPost,
    User,
    UserAccountType,
    UserPost,
    UserSession,
)
from homecontrol_api.exceptions import AuthenticationError
from homecontrol_api.service import HomeControlAPIService, get_homecontrol_api_service

auth = APIRouter(prefix="/auth", tags=["auth"])


async def get_token_from_header(authorization: Annotated[str, Header()]):
    """Returns bearer access token obtained from the request header"""
    auth = authorization.split(" ")
    if auth[0].lower() != "bearer" or len(auth) != 2:
        raise AuthenticationError("Invalid bearer token provided")
    return auth[1]


async def verify_current_user_session(
    api_service: Annotated[HomeControlAPIService, Depends(get_homecontrol_api_service)],
    access_token: Annotated[str, Depends(get_token_from_header)],
) -> User:
    """Returns the current user session (while also ensuring they are
    authenticated)"""
    return api_service.auth.authenticate_user_session(access_token=access_token)


async def verify_current_user(
    api_service: Annotated[HomeControlAPIService, Depends(get_homecontrol_api_service)],
    access_token: Annotated[str, Depends(get_token_from_header)],
) -> User:
    """Returns the current user (while also ensuring they are authenticated)"""
    return api_service.auth.authenticate_user(access_token=access_token)


def _create_user_dep(valid_account_type: UserAccountType):
    """Returns a dependency that gets the current user (while also ensuring
    they are an authenticated with a specified account type)"""

    async def user_dep(user: Annotated[User, Depends(verify_current_user)]) -> User:
        if user.account_type != valid_account_type:
            raise AuthenticationError("Insufficient credentials")
        return user

    return user_dep


verify_admin_user = _create_user_dep(UserAccountType.ADMIN)

AnySession = Annotated[UserSession, Depends(verify_current_user_session)]
AnyUser = Annotated[User, Depends(verify_current_user)]
AdminUser = Annotated[User, Depends(verify_admin_user)]
APIService = Annotated[HomeControlAPIService, Depends(get_homecontrol_api_service)]


@auth.get("/user", summary="Check authentication")
async def get_user(user: AnyUser) -> User:
    return user


@auth.post("/user", summary="Create user", status_code=status.HTTP_201_CREATED)
async def create_user(user_info: UserPost, api_service: APIService) -> User:
    return api_service.auth.create_user(user_info=user_info)


@auth.get("/users", summary="Obtain a list of all users")
async def get_users(user: AdminUser, api_service: APIService) -> list[User]:
    return api_service.auth._db_conn.users.get_all()


@auth.post("/login", summary="Login as a user")
async def login(login_data: LoginPost, api_service: APIService) -> UserSession:
    return api_service.auth.login(login_data)


@auth.post("/refresh", summary="Refresh a user session")
async def refresh(refresh_data: RefreshPost, api_service: APIService) -> UserSession:
    return api_service.auth.refresh_user_session(
        refresh_token=refresh_data.refresh_token
    )


@auth.post(
    "/logout",
    summary="Logout and invalidate the user session",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(current_session: AnySession, api_service: APIService) -> None:
    api_service.auth.logout(current_session.id)
