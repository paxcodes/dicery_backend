from datetime import datetime, timedelta
from typing import Optional
import string
import secrets

from jose import jwt

from .config import settings


def GenerateRoomCode() -> str:
    """Generates an alphanumeric 5-digit room code"""
    alphabet = string.ascii_uppercase + string.digits
    roomCode = "".join(secrets.choice(alphabet) for i in range(5))
    # TODO make sure that roomCode is unique/does not exist yet.
    return roomCode


def CreateAccessToken(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
