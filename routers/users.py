# Standard library imports
import os

# Third party imports
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.status import HTTP_401_UNAUTHORIZED

# Package imports
from core.config import SECRET_KEY, ALGORITHM
from services.security import verify_password, get_password_hash
from services.jwt import create_access_token
from models.users import UserRole, UserIn, UserOut, UserInDB
from models.tokens import Token, TokenData
from models.jwt import JWTPayload
from db.users import UsersDB


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


async def get_user(db: UsersDB, username: str):
    user = await db.get_user_by_email(username)
    return user


async def authenticate_user(db: UsersDB, username: str, password: str):
    user = await get_user(db, username)
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
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = await get_user(UsersDB(), username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(UsersDB(), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    payload = JWTPayload(sub=user.email)
    access_token = create_access_token(payload=payload)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/")
async def get_users(token: str = Depends(oauth2_scheme)):
    users = await UsersDB().get_all_users()
    return users


@router.get("/me", response_model=UserOut)
async def get_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user
