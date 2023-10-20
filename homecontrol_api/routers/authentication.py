from typing import Annotated
from fastapi import APIRouter, Depends

from homecontrol_api.authentication.schemas import LoginPost, RefreshPost, UserSession
from homecontrol_api.service import (
    HomeControlAPIService,
    get_homecontrol_api_service,
)

auth = APIRouter(prefix="/auth", tags=["auth"])


@auth.post("/login", summary="Login as a user")
async def login(
    login_data: LoginPost,
    api_service: Annotated[HomeControlAPIService, Depends(get_homecontrol_api_service)],
) -> UserSession:
    return api_service.auth.login(login_data)


@auth.post("/refresh", summary="Refresh a user session")
async def refresh(
    refresh_data: RefreshPost,
    api_service: Annotated[HomeControlAPIService, Depends(get_homecontrol_api_service)],
) -> UserSession:
    return api_service.auth.refresh_user_session(
        refresh_token=refresh_data.refresh_token
    )
