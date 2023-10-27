from enum import Enum
from typing import Optional

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
    enabled: bool


class UserPost(BaseModel):
    username: str
    password: str


class UserPatch(BaseModel):
    account_type: Optional[UserAccountType] = None
    enabled: Optional[bool] = None


class LoginPost(UserPost):
    long_lived: bool


class RefreshPost(BaseModel):
    refresh_token: str


class UserSession(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    user_id: StringUUID
    access_token: str
    refresh_token: str
