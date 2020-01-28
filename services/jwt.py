# Standard library imports
from datetime import datetime, timedelta

# Third party imports
import jwt
from pydantic import BaseModel

# Package imports
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models.jwt import JWTPayload


def create_access_token(*, payload: JWTPayload, expires_delta: timedelta = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
    payload.exp = expire
    encoded_jwt = jwt.encode(payload.dict(), str(SECRET_KEY), algorithm=ALGORITHM)
    return encoded_jwt
    