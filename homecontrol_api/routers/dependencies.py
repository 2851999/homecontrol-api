from typing import Annotated

from fastapi import Depends, Header, Request
from homecontrol_base.service.homecontrol_base import (
    HomeControlBaseService,
    create_homecontrol_base_service,
)
from homecontrol_api.authentication.schemas import User, UserAccountType, UserSession
from homecontrol_api.exceptions import AuthenticationError, InsufficientCredentialsError

from homecontrol_api.service import HomeControlAPIService, get_homecontrol_api_service


async def get_homecontrol_base_service(
    request: Request,
) -> HomeControlBaseService:
    """Constructs a base service using device managers loaded with the app"""

    with create_homecontrol_base_service(
        ac_manager=request.app.state.ac_manager,
        hue_manager=request.app.state.hue_manager,
        broadlink_manager=request.app.state.broadlink_manager,
    ) as service:
        yield service


# BaseService from homecontrol-base
BaseService = Annotated[HomeControlBaseService, Depends(get_homecontrol_base_service)]

# APIService from homecontrol-api
APIService = Annotated[HomeControlAPIService, Depends(get_homecontrol_api_service)]


# --------------------- DEPENDENCIES FOR AUTHENTICATION ---------------------


async def get_token_from_header(authorization: Annotated[str, Header()]):
    """Returns bearer access token obtained from the request header"""
    auth = authorization.split(" ")
    if auth[0].lower() != "bearer" or len(auth) != 2:
        raise AuthenticationError("Invalid bearer token provided")
    return auth[1]


AccessToken = Annotated[str, Depends(get_token_from_header)]


async def verify_current_user_session(
    api_service: APIService, access_token: AccessToken
) -> User:
    """Returns the current user session (while also ensuring they are
    authenticated)"""
    return api_service.auth.authenticate_user_session(access_token=access_token)


async def verify_current_user(
    api_service: APIService, access_token: AccessToken
) -> User:
    """Returns the current user (while also ensuring they are authenticated)"""
    return api_service.auth.authenticate_user(access_token=access_token)


def _create_user_dep(valid_account_type: UserAccountType):
    """Returns a dependency that gets the current user (while also ensuring
    they are an authenticated with a specified account type)"""

    async def user_dep(user: Annotated[User, Depends(verify_current_user)]) -> User:
        if user.account_type != valid_account_type:
            raise InsufficientCredentialsError("Insufficient credentials")
        return user

    return user_dep


verify_admin_user = _create_user_dep(UserAccountType.ADMIN)

AnySession = Annotated[UserSession, Depends(verify_current_user_session)]
AnyUser = Annotated[User, Depends(verify_current_user)]
AdminUser = Annotated[User, Depends(verify_admin_user)]
