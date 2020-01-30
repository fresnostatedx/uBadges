# Standard library imports

# Third party library imports
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

# Package imports
from db.users import UsersDB
from services.security import verify_password
from services.jwt import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def authenticate_user(email: str, password: str):
    user = await UsersDB().get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        token_data = decode_access_token(token)
    except:
        raise credentials_exception
    user = await UsersDB().get_user_by_email(token_data.username)
    if user is None:
        raise credentials_exception
    return user
