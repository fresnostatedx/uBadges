# Standard library
from datetime import datetime

# Third party libraries
from pydantic import BaseModel


class KeyBase(BaseModel):
    public_key: str


class KeyIn(KeyBase):
    private_key: str


class KeyOut(KeyBase):
    date_created: datetime
    date_revoked: datetime = None


class KeyInDB(KeyBase):
    private_key: str
    date_created: datetime
    date_revoked: datetime = None
