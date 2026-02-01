from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api import deps
from app.schemas.token import Token
from app.schemas.user import User
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    auth_service: AuthService = Depends(deps.get_auth_service),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    return auth_service.login(email=form_data.username, password=form_data.password)


@router.post("/test-token", response_model=User)
def test_token(current_user: User = Depends(deps.get_current_user)) -> User:
    return current_user
