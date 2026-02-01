from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# Shared properties
class TicketBase(BaseModel):
    status: Optional[str] = "open"


# Properties to receive on ticket creation
class TicketCreate(TicketBase):
    event_id: int
    order_id: int


# Properties to receive on ticket update
class TicketUpdate(TicketBase):
    pass


# Properties shared by models stored in DB
class TicketInDBBase(TicketBase):
    id: int
    uuid: UUID
    event_id: int
    order_id: int
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class TicketDTO(TicketInDBBase):
    pass


# Properties stored in DB
class TicketInDB(TicketInDBBase):
    pass
