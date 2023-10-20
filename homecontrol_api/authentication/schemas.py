from enum import Enum

from pydantic import BaseModel, ConfigDict

from homecontrol_api.core.types import StringUUID


class UserAccountType(str, Enum):
    DEFAULT = "default"
    ADMIN = "admin"


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    username: str
    account_type: UserAccountType


class UserPost(BaseModel):
    username: str
    password: str
    account_type: UserAccountType


class LoginPost(BaseModel):
    username: str
    password: str


class RefreshPost(BaseModel):
    refresh_token: str


class UserSession(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    user_id: StringUUID
    access_token: str
    refresh_token: str
