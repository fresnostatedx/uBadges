from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT
)
from pydantic import EmailStr

from db.issuers import IssuersDB
from db.badges import BadgesDB
from services.auth import get_current_user
from services.email import send_email
from models.issuers import IssuerIn, IssuerInDB, IssuerOut
from models.users import UserRole, UserInDB
from models.badges import BadgeIn, BadgeInDB

router = APIRouter()


@router.get("/", response_model=List[IssuerOut])
async def get_issuers(current_user: UserInDB = Depends(get_current_user)):
    if current_user.role == UserRole.ADMIN:
        issuers = await IssuersDB().get_all_issuers() 
    else:
        issuers = await IssuersDB().get_issuers_by_owner(current_user.id)
    return list(map(lambda issuer: issuer.dict(), issuers))


@router.get("/{issuer_id}", response_model=IssuerOut)
async def get_issuer(issuer_id: str, current_user: UserInDB = Depends(get_current_user)):
    issuer = await IssuersDB().get_issuer_by_id(issuer_id)
    if issuer is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return issuer.dict()


@router.post("/", status_code=HTTP_201_CREATED, response_model=IssuerOut)
async def create_issuer(response: Response, issuer: IssuerIn, current_user: UserInDB = Depends(get_current_user)):
   if current_user.role != UserRole.ADMIN:
       raise HTTPException(status_code=HTTP_403_FORBIDDEN)

   if await IssuersDB().get_issuer_by_name(issuer.name):
       raise HTTPException(
           status_code=HTTP_409_CONFLICT,
           detail=f"Issuer name {issuer.name} is already taken"
       )

   new_issuer = await IssuersDB().create_issuer(issuer)
   response.headers["Location"] = f"/issuers/{new_issuer.id}"
   return new_issuer.dict()


@router.put("/{issuer_id}", status_code=HTTP_204_NO_CONTENT)
async def update_issuer(issuer_id: str, issuer: IssuerIn, current_user: UserInDB = Depends(get_current_user)):
    issuer_in_db = await IssuersDB().get_issuer_by_id(issuer_id)

    if issuer_in_db is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
   
    if current_user.role != UserRole.ADMIN and issuer_in_db.owner_id != current_user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    issuer_in_db = await IssuersDB().get_issuer_by_name(issuer.name)
    if issuer_in_db and issuer_in_db.id != issuer_id:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=f"Issuer name {issuer.name} is already taken."
        ) 

    await IssuersDB().update_issuer(issuer_id, issuer)


@router.get("/{issuer_id}/badges", response_model=List[BadgeInDB])
async def get_badges_by_issuer(issuer_id: str, current_user: UserInDB = Depends(get_current_user)):
    if await IssuersDB().get_issuer_by_id(issuer_id) is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return await BadgesDB().get_badges_by_issuer_id(issuer_id)


@router.post("/{issuer_id}/badges", response_model=BadgeInDB, status_code=HTTP_201_CREATED)
async def create_badge(
    issuer_id,
    badge_in: BadgeIn,
    response: Response,
    current_user: UserInDB = Depends(get_current_user)
):
    if await IssuersDB().get_issuer_by_id(issuer_id) is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    if await BadgesDB().get_badge_by_name(badge_in.name):
        raise HTTPException(status_code=HTTP_409_CONFLICT)
    badge = await BadgesDB().create_badge(badge_in)
    response.headers["Location"] = f"/issuers/{issuer_id}/badges/{badge.id}"
    return badge


@router.get("/{issuer_id}/badges/{badge_id}", response_model=BadgeInDB)
async def get_badge_by_id(issuer_id: str, badge_id: str, current_user: UserInDB = Depends(get_current_user)):
    if await IssuersDB().get_issuer_by_id(issuer_id) is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    badge = await BadgesDB().get_badge_by_id(badge_id, issuer_id)
    if badge is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return badge


@router.put("/{issuer_id}/badges/{badge_id}", status_code=HTTP_204_NO_CONTENT)
async def update_badge(issuer_id: str, badge_id: str, badge_in: BadgeIn, current_user: UserInDB = Depends(get_current_user)):
    pass


# @router.post("/{issuer_id}/badges/{badge_id}/issue")
# async def issuer_badge(
#     issuer_id: str,
#     badge_id: str,
#     emails: List[EmailStr],
#     current_user: UserInDB = Depends(get_current_user)
# ):
#     issuer = await IssuersDB().get_issuer_by_id(issuer_id)
#     badge = await BadgesDB().get_badge_by_id(badge_id, issuer_id)
#     if issuer is None or badge is None:
#         raise HTTPException(status_code=HTTP_404_NOT_FOUND)


@router.get("/{issuer_id}/profile")
async def get_issuer_profile(issuer_id: str):
    issuer = await IssuersDB().get_issuer_by_id(issuer_id)
    if issuer is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    active_keys = [key for key in issuer.keys if key.date_revoked is None]
    active_key  = active_keys[0]

    return {
        "@context": [
            "https://w3id.org/openbadges/v2",
            "https://w3id.org/blockcerts/v2"
        ],
        "type": "Profile",
        "id": f"http://44.230.82.35:8000/issuers/{issuer.id}/profile",
        "name": issuer.name,
        "url": issuer.url,
        "introductionURL": f"http://44.230.82.35:8000/issuers/{issuer.id}/intro",
        "publicKey": [
            {
            "id": f"ecdsa-koblitz-pubkey:{active_key.public_key}",
            "created": active_key.date_created
            }
        ],
        "revocationList": f"http://44.230.82.35:8000/issuers/{issuer.id}/revocations",
        "image": issuer.image,
        "email": issuer.email
    }


@router.get("/{issuer_id}/revocations")
async def get_revocations(issuer_id: str):
    return {
        "@context": "https://w3id.org/openbadges/v2",
        "id": f"http://44.230.82.35:8000/issuers/{issuer_id}/revocations",
        "type": "RevocationList",
        "issuer": f"http://44.230.82.35:8000/issuers/{issuer_id}/profile",
        "revokedAssertions": [
            {
            "id": "urn:uuid:93019408-acd8-4420-be5e-0400d643954a",
            "revocationReason": "Honor code violation"
            },
            {
            "id": "urn:uuid:eda7d784-c03b-40a2-ac10-4857e9627329",
            "revocationReason": "Issued in error."
            }
        ]
    }


@router.post("/{issuer_id}/intro")
async def handle_invite_accept(issuer_id: str):
    return ""
