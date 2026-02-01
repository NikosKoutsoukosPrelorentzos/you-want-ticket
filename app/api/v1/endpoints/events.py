from fastapi import APIRouter, Depends, HTTPException

from app.api import deps
from app.core.logger import setup_logger
from app.dtos.event_dto import EventDTO, EventCreate
from app.dtos.user_dto import UserDTO
from app.services.event_service import EventService

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/")
def create_event(
        event_create_request: EventCreate,
        event_service: EventService = Depends(deps.get_event_service),
        current_user: UserDTO = Depends(deps.get_current_active_user)
) -> EventDTO:
    try:
        logger.info(f"Creating event for user: {current_user.email}")
        return event_service.create_event(event_create_request, current_user.uuid)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
