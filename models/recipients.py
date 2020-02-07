# Standard library
from datetime import datetime
from typing import List, Dict

# Third party libraries
from pydantic import BaseModel, EmailStr, HttpUrl


class RecipientBase(BaseModel):
    name: str
    email: EmailStr


class RecipientIn(RecipientBase):
    pass


class RecipientInDB(RecipientBase):
    id: str
    certs: List[HttpUrl]
    addresses: Dict[str, str]