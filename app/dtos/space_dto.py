from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.dtos.area_dto import AreaCreate, AreaDTO


class SpaceBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner_uuid: Optional[UUID] = None


class SpaceCreate(SpaceBase):
    name: str
    areas: Optional[List[AreaCreate]] = None


class SpaceUpdate(SpaceBase):
    pass


class SpaceInDBBase(SpaceBase):
    uuid: UUID
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


class SpaceDTO(SpaceInDBBase):
    areas: Optional[List[AreaDTO]] = None


class SpaceInDB(SpaceInDBBase):
    pass
