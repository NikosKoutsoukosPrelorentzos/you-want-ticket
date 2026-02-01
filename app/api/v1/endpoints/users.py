from fastapi import APIRouter, Depends

from app.api import deps
from app.schemas.user import User, UserCreate
from app.services.user_service import UserService

router = APIRouter()


@router.post("/", response_model=User)
def create_user(
    *,
    user_service: UserService = Depends(deps.get_user_service),
    user_in: UserCreate,
) -> User:
    return user_service.create_user(user_in=user_in)


@router.get("/me", response_model=User)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> User:
    return current_user
