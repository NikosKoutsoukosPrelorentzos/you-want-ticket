import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum as SAEnum, Float
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base
from app.enums.event_status import EventStatus
from app.enums.event_type import EventType


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    type: EventType = Column(SAEnum(EventType), index=True)
    title = Column(String, index=True)
    description = Column(String)
    owner_uuid = Column(UUID(as_uuid=True), ForeignKey("user.uuid"))
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime, index=True)
    status: EventStatus = Column(SAEnum(EventStatus), default=EventStatus.SCHEDULED)
    location = Column(String, index=True)
    available_number_of_tickets = Column(Integer)
    starting_price = Column(Float)
    space_uuid = Column(UUID(as_uuid=True), ForeignKey("space.uuid"))
