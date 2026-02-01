from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core import security
from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token, TokenPayload
from app.schemas.user import User


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def login(self, email: str, password: str) -> Token:
        user = self._authenticate_user(email=email, password=password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        elif not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user = self.user_repository.get_by_id(user_id=token_data.sub)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return User.model_validate(user)

    def _authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_email(email=email)
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return User.model_validate(user)
