from contextlib import asynccontextmanager
from importlib.metadata import version

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from homecontrol_base.aircon.manager import ACManager
from homecontrol_base.broadlink.manager import BroadlinkManager
from homecontrol_base.database.homecontrol_base.database import (
    database as homecontrol_base_db,
)
from homecontrol_base.hue.manager import HueManager

from homecontrol_api.database.database import database as homecontrol_api_db
from homecontrol_api.exceptions import APIError
from homecontrol_api.routers.auth import auth
from homecontrol_api.routers.devices.aircon import aircon
from homecontrol_api.service import create_homecontrol_api_service


async def lifespan(app: FastAPI):
    # Ensure all tables in database are created
    homecontrol_base_db.create_tables()
    homecontrol_api_db.create_tables()

    # Delete any expired user sessions
    with create_homecontrol_api_service() as service:
        service.auth.delete_all_expired_sessions()

    # Load and add managers (keeps devices in memory to keep authentication
    # - specifically needed for Midea AC units as the authentication takes
    # a while)

    # Load all immediately
    app.state.ac_manager: ACManager = ACManager(lazy_load=False)
    app.state.hue_manager: HueManager = HueManager()
    app.state.broadlink_manager: BroadlinkManager = BroadlinkManager()

    yield


app = FastAPI(lifespan=lifespan, version=version("homecontrol_api"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth)
app.include_router(aircon)


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Custom error handler to automatically convert anything based on
    APIError"""
    return await http_exception_handler(
        request, HTTPException(status_code=exc.status_code, detail=str(exc))
    )