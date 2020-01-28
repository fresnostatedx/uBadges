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
from models.users import User, UserInDB, UserRole
from models.jwt import JWTPayload
from models.tokens import Token, TokenData

fake_user_db = {
    "bob": {
        "username": "bob",
        "email": "bob@example.com",
        "hashed_password": "$2b$12$pc2RQy824XbVm7ZiOeR/F.9cwh6cbC9zOn5uHFp0mB/2bjq5LPsdC",
        "role": UserRole.ADMIN
    },
    "alice": {
        "username": "alice",
        "email": "alice@example.com",
        "hashed_password": "$2b$12$pc2RQy824XbVm7ZiOeR/F.9cwh6cbC9zOn5uHFp0mB/2bjq5LPsdC",
        "role": UserRole.OWNER
    }
}


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not User:
        return False
    if not verify_password(password, user.hashed_password):
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
    user = get_user(fake_user_db, username=token_data.username)
    if not user:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_user_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    payload = JWTPayload(sub=user.username)
    access_token = create_access_token(payload=payload)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/")
async def get_users(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
