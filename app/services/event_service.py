from datetime import datetime
from typing import Optional, List

from apscheduler.schedulers.base import BaseScheduler
from fastapi import HTTPException
from sqlalchemy import UUID

from app.core.logger import setup_logger
from app.dtos.event_dto import EventCreate, EventDTO
from app.enums.event_status import EventStatus
from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.enums.event_type import EventType

logger = setup_logger(__name__)


class EventService:
    def __init__(self, event_repository: EventRepository, scheduler: BaseScheduler = None):
        self.scheduler = scheduler
        self.event_repository = event_repository

    def create_event(self, event_create_request: EventCreate, user_uuid: UUID) -> EventDTO:
        self._validations(event_create_request)
        db_event = self.event_repository.create_event(event_create_request, user_uuid)
        try:
            self.scheduler.add_job(
                self._start_event(db_event.uuid),
                "date",
                run_date=event_create_request.start_date,
                args=[db_event.uuid],
                id=f"{db_event.uuid}_start",
                replace_existing=True
            )
            self.scheduler.add_job(
                self._end_event(db_event.uuid),
                "date",
                run_date=event_create_request.end_date,
                args=[db_event.uuid],
                id=f"{db_event.uuid}_end",
                replace_existing=True
            )
        except Exception as e:
            logger.error(f"Failed to schedule event jobs: {e}")
            self.event_repository.rollback()
            raise HTTPException(status_code=500, detail="Internal server error")
        self.event_repository.commit()
        return EventDTO.model_validate(db_event)

    @staticmethod
    def _validations(event_create_request: EventCreate):
        if event_create_request.start_date > event_create_request.end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        if event_create_request.available_number_of_tickets <= 0:
            raise HTTPException(status_code=400, detail="Available number of tickets must be greater than 0")

    def get_event_by_uuid(self, event_uuid: UUID) -> EventDTO:
        db_event = self.event_repository.get_event_by_uuid(event_uuid)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        return EventDTO.model_validate(db_event)

    def get_events_by_start_date(self, start_date: datetime) -> list[EventDTO]:
        db_events = self.event_repository.get_events_by_start_date(start_date)
        return [EventDTO.model_validate(event) for event in db_events]

    def get_events_by_location(self, location: str) -> list[EventDTO]:
        db_events = self.event_repository.get_events_by_location(location)
        return [EventDTO.model_validate(event) for event in db_events]

    def remove_available_tickets(self, event_uuid: UUID, number_of_tickets: int):
        result = self.event_repository.remove_available_tickets(event_uuid, number_of_tickets)
        if result == 0:
            raise HTTPException(status_code=409, detail="Event is sold out")
        return

    def add_available_tickets(self, event_uuid: UUID, number_of_tickets: int):
        result = self.event_repository.add_available_tickets(event_uuid, number_of_tickets)
        if result == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        return

    def get_all_events(
            self,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            event_type: Optional[EventType] = None,
            location: Optional[str] = None
    ) -> List[EventDTO]:
        db_events = self.event_repository.get_all_events(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            location=location
        )
        return [EventDTO.model_validate(event) for event in db_events]

    def _start_event(self, event_uuid: UUID) -> int:
        logger.info(f"Starting event with UUID: {event_uuid}")
        result = self.event_repository.start_event(event_uuid)
        if result == 0:
            logger.warning(f"Event not found or not in SCHEDULED state: {event_uuid}")
        return result

    def _end_event(self, event_uuid: UUID) -> int:
        logger.info(f"Ending event with UUID: {event_uuid}")
        result = self.event_repository.end_event(event_uuid)
        if result == 0:
            logger.warning(f"Event not found or not in ACTIVE state: {event_uuid}")
        return result

    def cancel_event(self, event_uuid: UUID, user_uuid: UUID):
        logger.info(f"Canceling event with UUID: {event_uuid}")
        db_event: Event = self.event_repository.get_event_by_uuid(event_uuid)
        if db_event.owner_uuid != user_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this event")
        if db_event.status != EventStatus.SCHEDULED:
            raise HTTPException(status_code=409, detail="Event is not scheduled")
        result: int = self.event_repository.cancel_event(event_uuid)
        if result == 0:
            raise HTTPException(status_code=404, detail="Event not found")

        if self.scheduler:
            try:
                self.scheduler.remove_job(f"{event_uuid}_start")
                self.scheduler.remove_job(f"{event_uuid}_end")
            except Exception as e:
                logger.warning(f"Could not remove scheduled jobs for event {event_uuid}: {e}")
        return
