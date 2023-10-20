from fastapi import status


class APIError(Exception):
    """Custom error for homecontrol-api to be picked up by a custom exception
    handler"""

    status_code: int

    def __init__(self, message) -> None:
        super().__init__(message)


class AuthenticationError(APIError):
    """Raised when authentication fails"""

    status_code = status.HTTP_401_UNAUTHORIZED
