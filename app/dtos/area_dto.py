from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AreaBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    space_uuid: Optional[UUID] = None
    capacity: Optional[int] = None
    price_multiplier: Optional[float] = None


class AreaCreate(AreaBase):
    name: str
    capacity: int


class AreaUpdate(AreaBase):
    pass


class AreaInDBBase(AreaBase):
    id: int
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


class AreaDTO(AreaInDBBase):
    pass


class AreaInDB(AreaInDBBase):
    pass
