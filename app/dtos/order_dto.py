from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.enums.order_status import OrderStatus


class OrderBase(BaseModel):
    status: Optional[OrderStatus]
    number_of_tickets: Optional[int] = None
    amount: Optional[float] = None


# Properties to receive on order creation
class OrderCreate(OrderBase):
    event_uuid: UUID
    number_of_tickets: int


# Properties to receive on order update
class OrderUpdate(OrderBase):
    pass


# Properties shared by models stored in DB
class OrderInDBBase(OrderBase):
    uuid: UUID
    owner_uuid: UUID
    event_uuid: UUID
    created_date: datetime
    updated_date: datetime

    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class OrderDTO(OrderInDBBase):
    pass


# Properties stored in DB
class OrderInDB(OrderInDBBase):
    pass
