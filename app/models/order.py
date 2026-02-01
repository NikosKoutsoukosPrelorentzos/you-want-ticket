import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base
from app.enums.order_status import OrderStatus


class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    owner_uuid = Column(UUID(as_uuid=True), ForeignKey("user.uuid"))
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(SAEnum(OrderStatus), default=OrderStatus.IN_PROGRESS)
    event_uuid = Column(UUID(as_uuid=True), ForeignKey("event.uuid"))
    number_of_tickets = Column(Integer)
