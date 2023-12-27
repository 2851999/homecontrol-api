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
from homecontrol_api.routers.actions.broadlink import broadlink_actions
from homecontrol_api.routers.auth import auth
from homecontrol_api.routers.devices.aircon import aircon
from homecontrol_api.routers.devices.broadlink import broadlink
from homecontrol_api.routers.devices.hue import hue
from homecontrol_api.routers.rooms import rooms
from homecontrol_api.routers.scheduler import scheduler
from homecontrol_api.routers.temperature import temperature
from homecontrol_api.scheduler.core import Scheduler
from homecontrol_api.service.homecontrol_api import create_homecontrol_api_service


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Used to setup the database, delete expired sessions and initialise
    devices when starting"""

    # Ensure all tables in database are created
    homecontrol_base_db.create_tables()
    homecontrol_api_db.create_tables()

    # Delete any expired user sessions
    with create_homecontrol_api_service() as service:
        service.auth.delete_all_expired_sessions()

    # Load and add managers (keeps devices in memory to keep authentication
    # - specifically needed for Midea AC units as the authentication takes
    # a while)

    app_instance.state.ac_manager: ACManager = ACManager(lazy_load=False)
    # Load all immediately
    await app_instance.state.ac_manager.initialise_all_devices()
    app_instance.state.hue_manager: HueManager = HueManager()
    app_instance.state.broadlink_manager: BroadlinkManager = BroadlinkManager()

    # Scheduler
    app_instance.state.scheduler = Scheduler()
    app_instance.state.scheduler.start()

    yield

    app_instance.state.scheduler.stop()


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
app.include_router(hue)
app.include_router(broadlink)
app.include_router(rooms)
app.include_router(temperature)
app.include_router(broadlink_actions)
app.include_router(scheduler)


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Custom error handler to automatically convert anything based on
    APIError"""
    return await http_exception_handler(
        request, HTTPException(status_code=exc.status_code, detail=str(exc))
    )
