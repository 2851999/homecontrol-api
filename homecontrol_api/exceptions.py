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


class InsufficientCredentialsError(APIError):
    """Raised when a user has insufficient credentials to access a resource"""

    status_code = status.HTTP_403_FORBIDDEN
