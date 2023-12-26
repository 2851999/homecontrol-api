from fastapi import APIRouter

from homecontrol_api.routers.actions.broadlink import broadlink_actions

actions = APIRouter(prefix="/actions", tags=["actions"])

actions.include_router(broadlink_actions)
