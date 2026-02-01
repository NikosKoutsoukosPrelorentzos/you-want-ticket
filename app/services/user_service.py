from typing import Optional

from fastapi import HTTPException

from app.models.user import User as UserModel
from app.repositories.user_repository import UserRepository
from app.dtos.user_dto import UserDTO, UserCreate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user_in: UserCreate) -> UserDTO:
        user = self.user_repository.get_by_email(email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
        created_user = self.user_repository.create(user_in)
        return UserDTO.model_validate(created_user)

    def get_user_by_email(self, email: str) -> Optional[UserDTO]:
        user = self.user_repository.get_by_email(email)
        if user:
            return UserDTO.model_validate(user)
        return None
