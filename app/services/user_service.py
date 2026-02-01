from typing import Optional

from fastapi import HTTPException

from app.core.logger import setup_logger
from app.models.user import User as UserModel
from app.repositories.user_repository import UserRepository
from app.dtos.user_dto import UserDTO, UserCreate

logger = setup_logger(__name__)

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user_in: UserCreate) -> UserDTO:
        logger.info(f"Creating new user with email: {user_in.email}")
        user = self.user_repository.get_by_email(email=user_in.email)
        if user:
            logger.warning(f"User creation failed: Email {user_in.email} already exists")
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
        created_user = self.user_repository.create(user_in)
        logger.info(f"User created successfully: {created_user.uuid}")
        return UserDTO.model_validate(created_user)

    def get_user_by_email(self, email: str) -> Optional[UserDTO]:
        logger.info(f"Fetching user by email: {email}")
        user = self.user_repository.get_by_email(email)
        if user:
            return UserDTO.model_validate(user)
        logger.info(f"User not found with email: {email}")
        return None
