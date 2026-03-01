import uuid
from typing import Any

from sqlalchemy import Boolean, Column, Integer, String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base
from app.enums.user_role import UserRole


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active: Any = Column(Boolean(), default=True)
    user_role: UserRole = Column(SAEnum(UserRole), default=UserRole.CUSTOMER)
