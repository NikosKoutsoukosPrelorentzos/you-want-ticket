import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base
from app.enums.ticket_status import TicketStatus


class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(SAEnum(TicketStatus), default=TicketStatus.SCHEDULED)
    event_uuid = Column(UUID, ForeignKey("event.uuid"))
    order_uuid = Column(UUID, ForeignKey("order.uuid"))
