
from enum import Enum
from typing import Annotated, Union
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict


class UserAccountType(str, Enum):
    DEFAULT = "default"
    ADMIN = "admin"

def convert_uuid_to_string(id: Union[UUID, str]):
    """Converts a UUID type to id"""
    if isinstance(id, UUID):
        return str(id)
    else:
        return id
    
StringUUID = Annotated[str, BeforeValidator(convert_uuid_to_string)]

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: StringUUID
    name: str
    account_type: UserAccountType

class UserPost(BaseModel):
    name: str
    password: str
    account_type: UserAccountType