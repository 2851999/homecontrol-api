from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler

from homecontrol_api.exceptions import APIError
from homecontrol_api.routers.authentication import auth

app = FastAPI()

app.include_router(auth)


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Custom error handler to automatically convert anything based on
    APIError"""
    return await http_exception_handler(
        request, HTTPException(status_code=exc.status_code, detail=str(exc))
    )
