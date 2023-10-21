from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from homecontrol_base.database.homecontrol_base.database import (
    database as homecontrol_base_db,
)

from homecontrol_api.database.database import database as homecontrol_api_db
from homecontrol_api.exceptions import APIError
from homecontrol_api.routers.authentication import auth
from homecontrol_api.service import create_homecontrol_api_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all tables in database are created
    homecontrol_base_db.create_tables()
    homecontrol_api_db.create_tables()

    # Delete any expired user sessions
    with create_homecontrol_api_service() as service:
        service.auth.delete_all_expired_sessions()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth)


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Custom error handler to automatically convert anything based on
    APIError"""
    return await http_exception_handler(
        request, HTTPException(status_code=exc.status_code, detail=str(exc))
    )
