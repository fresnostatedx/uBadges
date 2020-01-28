# Standard library imports
from enum import Enum, unique

# Third party library imports
from pydantic import BaseModel

class UserRole(str, Enum):
    ADMIN = "admin"
    OWNER = "owner"
    MANAGER = "manager"


class User(BaseModel):
    username: str
    email: str
    role: UserRole


class UserInDB(User):
    hashed_password: str
