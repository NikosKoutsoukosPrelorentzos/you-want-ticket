import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class Place(Base):
    __tablename__ = "place"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    address = Column(String)
    owner_uuid = Column(UUID(as_uuid=True), ForeignKey("user.uuid"))
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    capacity = Column(Integer)
