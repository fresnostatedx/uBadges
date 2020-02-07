# Standard library
from datetime import datetime
from typing import List

# Third party libraries
from pydantic import BaseModel


class InviteBase(BaseModel):
    issuer_id: str
    recipient_id: str


class InviteInCreate(InviteBase):
    badge_id: str


class InviteInDB(InviteBase):
    id: str
    nonce: str
    badges: List[str]


class InviteAcceptResponse(BaseModel):
    nonce: str
    bitcoinAddress: str