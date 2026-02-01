from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.enums.event_status import EventStatus
from app.enums.event_type import EventType


# Shared properties
class EventBase(BaseModel):
    type: Optional[EventType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[EventStatus] = EventStatus.SCHEDULED
    location: Optional[str] = None
    available_number_of_tickets: Optional[int] = None


# Properties to receive on event creation
class EventCreate(EventBase):
    type: EventType
    title: str
    start_date: datetime
    end_date: datetime
    location: str
    available_number_of_tickets: int


# Properties to receive on event update
class EventUpdate(EventBase):
    pass


# Properties shared by models stored in DB
class EventInDBBase(EventBase):
    id: int
    uuid: UUID
    owner_id: int
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class EventDTO(EventInDBBase):
    pass


# Properties stored in DB
class EventInDB(EventInDBBase):
    pass
