# Standard library
from datetime import datetime
from typing import List

# Third party libraries
from pydantic import BaseModel

class SignatureLine(BaseModel):
    type: List[str] = ["SignatureLine", "Extension"]
    name: str
    image: str
    jobTitle: str


class Criteria(BaseModel):
    narrative: str


class BadgeIn(BaseModel):
    issuer_id: str
    name: str
    description: str
    criteria: Criteria
    image: str
    signatureLines: List[SignatureLine]
    template: int


class BadgeInDB(BadgeIn):
    id: str
    