# Standard library imports
from datetime import datetime

# Third party library imports
from pydantic import BaseModel

class JWTPayload(BaseModel):
    exp: datetime = datetime.utcnow()
    sub: str