from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    uuid: UUID
    model_config = ConfigDict(from_attributes=True)


class UserDTO(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
