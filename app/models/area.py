import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float

from app.db.base_class import Base


class Area(Base):
    __tablename__ = "area"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    name = Column(String, index=True)
    description = Column(String)
    space_uuid = Column(UUID(as_uuid=True), ForeignKey("space.uuid"))
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    capacity = Column(Integer)
    price_multiplier = Column(Float)
