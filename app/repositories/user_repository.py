from typing import Optional
from uuid import UUID

from app.core.security import get_password_hash
from app.models.user import User
from app.dtos.user_dto import UserCreate
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def create(self, user_in: UserCreate) -> User:
        db_obj = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            is_active=user_in.is_active,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_uuid(self, user_uuid: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.uuid == user_uuid).first()
