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


class UsernameAlreadyExistsError(APIError):
    """Raised when attempting to create a user with a username that already exists"""

    status_code = status.HTTP_409_CONFLICT


class NameAlreadyExistsError(APIError):
    """Raised when attempting to create an entity with a name that already exists"""

    status_code = status.HTTP_409_CONFLICT


class DeviceNotFoundError(APIError):
    """Raised when attempting to obtain a device but it isn't found"""

    status_code = status.HTTP_404_NOT_FOUND


class TooManyRequestsError(APIError):
    """Raised when a request fails due to a rate limit"""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
