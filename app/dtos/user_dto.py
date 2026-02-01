from typing import Optional

import uuid
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
    id: Optional[int] = None
    uuid: Optional[uuid] = None
    model_config = ConfigDict(from_attributes=True)


class UserDTO(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
