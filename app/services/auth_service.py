from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core import security
from app.core.config import settings
from app.core.logger import setup_logger
from app.repositories.user_repository import UserRepository
from app.dtos.token_dto import TokenDTO, TokenPayload
from app.dtos.user_dto import UserDTO

logger = setup_logger(__name__)

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def login(self, email: str, password: str) -> TokenDTO:
        logger.info(f"Attempting login for user: {email}")
        user = self._authenticate_user(email=email, password=password)
        if not user:
            logger.warning(f"Login failed for user: {email} - Incorrect credentials")
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        elif not user.is_active:
            logger.warning(f"Login failed for user: {email} - Inactive user")
            raise HTTPException(status_code=400, detail="Inactive user")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            user.uuid, expires_delta=access_token_expires
        )
        logger.info(f"Login successful for user: {email}")
        return TokenDTO(access_token=access_token, token_type="bearer")

    def get_current_user(self, token: str) -> UserDTO:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except (JWTError, ValidationError) as e:
            logger.error(f"Token validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user = self.user_repository.get_by_uuid(user_uuid=token_data.sub)

        if not user:
            logger.warning(f"User not found for token subject: {token_data.sub}")
            raise HTTPException(status_code=404, detail="User not found")
        return UserDTO.model_validate(user)

    def _authenticate_user(self, email: str, password: str) -> Optional[UserDTO]:
        user = self.user_repository.get_by_email(email=email)
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return UserDTO.model_validate(user)
