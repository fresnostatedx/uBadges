# Standard library
from datetime import datetime
from typing import List, Dict

# Third party libraries
from pydantic import BaseModel, EmailStr, HttpUrl

# Package
from models.keys import KeyIn, KeyOut, KeyInDB


class IssuerBase(BaseModel):
    name: str
    email: EmailStr
    url: str 
    image: str
    owner_id: str


class IssuerIn(IssuerBase):
    key: KeyIn 


class IssuerInDB(IssuerBase):
    id: str
    keys: List[KeyInDB]
    revocations: List[str]


class IssuerOut(IssuerBase):
    id: str
    keys: List[KeyOut]
    revocations: List[str]
