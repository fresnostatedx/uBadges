# Standard library imports
import os

# Third party imports
import jwt
from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

# Package imports
from services.auth import get_current_user
from models.users import UserRole, UserIn, UserOut, UserInDB
from db.users import UsersDB


router = APIRouter()


@router.get("/")
async def get_users(token: str = Depends(get_current_user)):
    users = await UsersDB().get_all_users()
    return users


@router.get("/me", response_model=UserOut)
async def get_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user
