from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api import deps
from app.core.logger import setup_logger
from app.dtos.event_dto import EventDTO, EventCreate
from app.dtos.user_dto import UserDTO
from app.services.event_service import EventService
from app.enums.event_type import EventType

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
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/all")
def get_all_events(
        start_date: Optional[datetime] = Query(None, description="Filter by start date (>=)"),
        end_date: Optional[datetime] = Query(None, description="Filter by end date (<=)"),
        event_type: Optional[EventType] = Query(None, description="Filter by event type"),
        location: Optional[str] = Query(None, description="Filter by location (partial match)"),
        event_service: EventService = Depends(deps.get_event_service),
        current_user: UserDTO = Depends(deps.get_current_active_user)
) -> list[EventDTO]:
    try:
        logger.info(f"Getting all events for user: {current_user.email} with filters: start={start_date}, end={end_date}, type={event_type}, loc={location}")
        return event_service.get_all_events(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            location=location
        )
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
