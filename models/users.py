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


class UserInCreate(UserBase):
    password: str


class UserInUpdate(BaseModel):
    email: EmailStr = None
    role: UserRole = None
    password: str = None 


class UserOut(UserBase):
    id: str


class UserInDB(UserBase):
    id: str
    hashed_password: str
