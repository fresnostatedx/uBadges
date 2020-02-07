from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT
)

from db.recipients import RecipientsDB
from services.auth import get_current_user
from models.users import UserRole, UserInDB
from models.recipients import RecipientIn, RecipientInDB

router = APIRouter()


@router.get("/", response_model=List[RecipientInDB])
async def get_all_recipients(prefix: str = None, current_user: UserInDB = Depends(get_current_user)):
    return await RecipientsDB().get_all_recipients()


@router.get("/{recipient_id}", response_model=RecipientInDB)
async def get_recipient(recipient_id: str, current_user: UserInDB = Depends(get_current_user)):
    recipient = await RecipientsDB().get_recipients_by_id(recipient_id)
    if recipient is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return recipient


@router.post("/", response_model=RecipientInDB, status_code=HTTP_201_CREATED)
async def create_recipient(
    recipient: RecipientIn, 
    response: Response, 
    current_user: UserInDB = Depends(get_current_user)
):
    if not await RecipientsDB().get_recipient_by_email(recipient.email) is None:
        raise HTTPException(status_code=HTTP_409_CONFLICT)
    recipient = await RecipientsDB().create_recipient(recipient)
    response.headers["Location"] = f"/recipients/{recipient.id}"
    return recipient


@router.put("/{recipient_id}")
async def update_recipient(recipient_id: str, current_user: UserInDB = Depends(get_current_user)):
    pass
