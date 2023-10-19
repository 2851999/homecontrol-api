from datetime import datetime, timedelta
from typing import Any

import bcrypt
import jwt

from homecontrol_api.exceptions import AuthenticationError


def hash_password(password: str) -> bytes:
    """Returns the hash of a password"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(password: str, hash: bytes) -> bool:
    """Returns whether a password matches it's hash"""
    return bcrypt.checkpw(password.encode("utf-8"), hash)


def generate_jwt(payload: dict[str, Any], key: str, seconds_to_expire: int):
    """Generates a jwt given the payload and key

    Args:
        payload (dict[str, Any]): Payload to store in the token ('exp' will be
                                  added automatically)
        key (str): Key to encrypt with
        seconds_to_expire (str): Time in seconds before the token expires
    """
    payload["exp"] = datetime.utcnow() + timedelta(seconds=seconds_to_expire)
    return jwt.encode(payload=payload, key=key, algorithm="HS256")


def verify_jwt(token: str, key: str) -> dict[str, Any]:
    """Decodes and verifies a JWT using its expiry time

    Args:
        token (str): JWT token
        key (str): Key to decrypt with

    Returns:
        dict[str, Any]: Payload of the token

    Raises:
        AuthenticationError: If the token has expired
    """
    try:
        payload = jwt.decode(jwt=token, key=key, algorithms=["HS256"])
    except jwt.exceptions.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    return payload
