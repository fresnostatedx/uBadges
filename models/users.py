# Standard library imports
from enum import Enum, unique

# Third party library imports
from pydantic import BaseModel, EmailStr


@unique
class UserRole(str, Enum):
    ADMIN = "admin"
    OWNER = "owner"
    MANAGER = "manager"


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: str


class UserInDB(UserBase):
    id: str
    hashed_password: str
