from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# Shared properties
class OrderBase(BaseModel):
    status: Optional[str] = "open"
    number_of_tickets: Optional[int] = None


# Properties to receive on order creation
class OrderCreate(OrderBase):
    event_id: int
    number_of_tickets: int


# Properties to receive on order update
class OrderUpdate(OrderBase):
    pass


# Properties shared by models stored in DB
class OrderInDBBase(OrderBase):
    id: int
    uuid: UUID
    owner_id: int
    event_id: int
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class OrderDTO(OrderInDBBase):
    pass


# Properties stored in DB
class OrderInDB(OrderInDBBase):
    pass
