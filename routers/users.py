# Standard library imports
import os
from typing import List

# Third party imports
import jwt
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN, 
    HTTP_404_NOT_FOUND, 
    HTTP_409_CONFLICT
)

# Package imports
from db.users import UsersDB
from services.auth import get_current_user
from models.users import (
    UserRole,
    UserInCreate, 
    UserInUpdate,
    UserInDB,
    UserOut
)


router = APIRouter()


@router.get("/", response_model=List[UserOut])
async def get_users(role: UserRole= None, current_user: UserInDB = Depends(get_current_user)):
    if role:
        users = await UsersDB().get_users_by_role(role)
    else:
        users = await UsersDB().get_all_users()
    return users


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, current_user: UserInDB = Depends(get_current_user)):
    user = await UsersDB().get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return user


@router.post("/", status_code=HTTP_201_CREATED, response_model=UserOut)
async def create_user(user: UserInCreate, response: Response, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    if await UsersDB().get_user_by_email(user.email):
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=f"Email {user.email} is already taken"
        )

    user = await UsersDB().create_user(**user.dict())
    response.headers["Location"] = f"/users/{user.id}"
    return user


@router.put("/{user_id}", status_code=HTTP_204_NO_CONTENT)
async def update_user(user_id: str, user: UserInUpdate, current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    if await UsersDB().get_user_by_id(user_id) is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    try:
        update_user = await UsersDB().update_user(user_id, **user.dict())
    except:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, 
            detail=f"Email {user.email} is already taken"
        )
