from fastapi import APIRouter, Depends, HTTPException

from app.api import deps
from app.core.logger import setup_logger
from app.dtos.user_dto import UserDTO, UserCreate
from app.services.user_service import UserService

router = APIRouter()
logger = setup_logger(__name__)

@router.post("/", response_model=UserDTO)
def create_user(
    *,
    user_service: UserService = Depends(deps.get_user_service),
    user_in: UserCreate,
) -> UserDTO:
    try:
        logger.info("Received request to create new user")
        return user_service.create_user(user_in=user_in)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(f"Error scanning ticket: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me", response_model=UserDTO)
def read_user_me(
    current_user: UserDTO = Depends(deps.get_current_active_user),
) -> UserDTO:
    logger.info(f"Fetching current user profile for: {current_user.email}")
    return current_user
