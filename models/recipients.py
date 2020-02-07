# Standard library
from datetime import datetime
from typing import List

# Third party libraries
from pydantic import BaseModel, EmailStr, HttpUrl


class AddressAssociation(BaseModel):
    issuer_id: str
    public_key: str


class RecipientBase(BaseModel):
    name: str
    email: EmailStr


class RecipientIn(RecipientBase):
    pass


class RecipientInDB(RecipientBase):
    id: str
    certs: List[HttpUrl]
    addresses: List[AddressAssociation]