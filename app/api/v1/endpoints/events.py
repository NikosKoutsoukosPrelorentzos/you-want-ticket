from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from starlette.responses import JSONResponse

from app.api import deps
from app.core.logger import setup_logger
from app.core.role_checker import organizer_checker
from app.dtos.event_dto import EventDTO, EventCreate, EventUpdate
from app.dtos.user_dto import UserDTO
from app.services.event_service import EventService
from app.enums.event_type import EventType

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/")
def create_event(
        event_create_request: EventCreate,
        event_service: EventService = Depends(deps.get_event_service),
        current_user: UserDTO = Depends(organizer_checker),
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
        logger.info(
            f"Getting all events for user: {current_user.email} with filters: start={start_date}, end={end_date}, type={event_type}, loc={location}")
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


@router.get("/{event_uuid}")
def get_event_by_uuid(
        event_uuid: UUID,
        event_service: EventService = Depends(deps.get_event_service),
        current_user: UserDTO = Depends(deps.get_current_active_user)
) -> EventDTO:
    try:
        logger.info(f"Getting event by UUID: {event_uuid} for user: {current_user.email}")
        return event_service.get_event_by_uuid(event_uuid)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{event_uuid}/cancel")
def cancel_event(
        event_uuid: UUID,
        event_service: EventService = Depends(deps.get_event_service),
        current_user: UserDTO = Depends(deps.get_current_active_user)
) -> JSONResponse:
    try:
        logger.info(f"Cancelling event with UUID: {event_uuid} for user: {current_user.email}")
        event_service.cancel_event(event_uuid, current_user.uuid)
        return JSONResponse(status_code=200, content={"message": "Event cancelled successfully"})
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{event_uuid}/update")
def update_event(
        event_uuid: UUID,
        event_update_request: EventUpdate,
        event_service: EventService = Depends(deps.get_event_service),
        current_user: UserDTO = Depends(organizer_checker)
) -> EventDTO:
    try:
        logger.info(f"Updating event with UUID: {event_uuid} for user: {current_user.email}")
        return event_service.update_event(event_uuid, event_update_request, current_user.uuid)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
