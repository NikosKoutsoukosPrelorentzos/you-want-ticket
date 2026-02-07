import uuid

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class Space(Base):
    __tablename__ = "space"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    description = Column(String)
    owner_uuid = Column(UUID(as_uuid=True), ForeignKey("user.uuid"))
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
