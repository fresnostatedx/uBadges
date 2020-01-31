# Standard library
from datetime import datetime
from typing import List

# Third party libraries
from pydantic import BaseModel, EmailStr, AnyUrl

# Package
from models.keys import KeyIn, KeyOut, KeyInDB


class IssuerBase(BaseModel):
    name: str
    email: EmailStr
    url: AnyUrl
    image: str
    owner_id: str


class IssuerInCreate(IssuerBase):
    key: KeyIn 


class IssuerInUpdate(BaseModel):
    name: str = None
    email: EmailStr = None
    url: AnyUrl = None
    image: str = None
    owner_id: str = None
    key: KeyIn = None


class IssuerOut(IssuerBase):
    id: str
    keys: List[KeyOut]
    revocations: List[str]


class IssuerInDB(IssuerBase):
    id: str
    keys: List[KeyInDB]
    revocations: List[str]
