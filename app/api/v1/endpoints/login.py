from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api import deps
from app.dtos.token_dto import TokenDTO
from app.dtos.user_dto import UserDTO
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login/access-token", response_model=TokenDTO)
def login_access_token(
    auth_service: AuthService = Depends(deps.get_auth_service),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenDTO:
    return auth_service.login(email=form_data.username, password=form_data.password)


@router.post("/test-token", response_model=UserDTO)
def test_token(current_user: UserDTO = Depends(deps.get_current_user)) -> UserDTO:
    return current_user
