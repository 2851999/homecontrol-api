from fastapi import FastAPI

from homecontrol_api.routers.authentication import auth

app = FastAPI()

app.include_router(auth)
