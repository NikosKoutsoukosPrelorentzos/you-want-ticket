from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.enums.ticket_status import TicketStatus


# Shared properties
class TicketBase(BaseModel):
    status: Optional[TicketStatus]


# Properties to receive on ticket creation
class TicketCreate(TicketBase):
    event_uuid: UUID
    order_uuid: UUID
    owner_uuid: UUID


# Properties to receive on ticket update
class TicketUpdate(TicketBase):
    ticket_uuid: UUID


# Properties shared by models stored in DB
class TicketInDBBase(TicketBase):
    uuid: UUID
    event_uuid: UUID
    order_uuid: UUID
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class TicketDTO(TicketInDBBase):
    # QR code is returned as a Base64-encoded PNG string (data only, no mime prefix)
    qr_code: Optional[str] = None


# Properties stored in DB
class TicketInDB(TicketInDBBase):
    pass
