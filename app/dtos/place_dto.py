from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaceBase(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None


class PlaceCreate(PlaceBase):
    name: str
    address: str
    capacity: int


class PlaceUpdate(PlaceBase):
    pass


class PlaceInDBBase(PlaceBase):
    uuid: UUID
    owner_uuid: UUID
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaceDTO(PlaceInDBBase):
    pass


class PlaceInDB(PlaceInDBBase):
    pass
