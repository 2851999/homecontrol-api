from typing import Annotated
from fastapi import APIRouter, Depends

from homecontrol_api.schemas import LoginPost, UserSession
from homecontrol_api.service import (
    HomeControlAPIService,
    create_homecontrol_api_service,
)

auth = APIRouter(prefix="/auth", tags=["auth"])


@auth.post("/login", summary="Login as a user")
async def login(
    login_data: LoginPost,
    api_service: Annotated[
        HomeControlAPIService, Depends(create_homecontrol_api_service)
    ],
) -> UserSession:
    return api_service.auth.login(login_data)
