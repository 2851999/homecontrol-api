from homecontrol_base.config.base import BaseConfig
from pydantic.dataclasses import dataclass


@dataclass
class APIConfigSecurityData:
    """API config for security"""

    jwt_key: str
    access_token_expiry: int
    refresh_token_expiry: int
    long_lived_refresh_token_expiry: int


@dataclass
class APIConfigData:
    """API config for homecontrol-api"""

    security: APIConfigSecurityData


class APIConfig(BaseConfig[APIConfigData]):
    """API config for homecontrol-api"""

    def __init__(self) -> None:
        super().__init__("api.json", APIConfigData)

    @property
    def security(self) -> APIConfigSecurityData:
        return self._data.security
