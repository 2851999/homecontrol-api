from typing import Optional

from pydantic import BaseModel


class Temperature(BaseModel):
    value: Optional[float]
