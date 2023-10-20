from typing import Annotated, Union
from uuid import UUID

from pydantic import BeforeValidator


def convert_uuid_to_string(id: Union[UUID, str]):
    """Converts a UUID type to id"""
    if isinstance(id, UUID):
        return str(id)
    else:
        return id


StringUUID = Annotated[str, BeforeValidator(convert_uuid_to_string)]
