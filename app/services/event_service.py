from datetime import datetime
from typing import Optional, List

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.base import BaseScheduler
from fastapi import HTTPException
from sqlalchemy import UUID

from app.core.logger import setup_logger
from app.dtos.event_dto import EventCreate, EventDTO, EventUpdate
from app.enums.event_status import EventStatus
from app.models.event import Event
from app.models.place import Place
from app.repositories.event_repository import EventRepository
from app.enums.event_type import EventType
from app.repositories.order_repository import OrderRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService

logger = setup_logger(__name__)


class EventService:
    def __init__(self, event_repository: EventRepository,
                 place_repository: PlaceRepository,
                 ticket_repository: TicketRepository,
                 order_repository: OrderRepository,
                 user_repository: UserRepository,
                 scheduler: Optional[BaseScheduler] = None):
        self.event_repository = event_repository
        self.scheduler = scheduler
        self.place_repository = place_repository
        self.ticket_repository = ticket_repository
        self.order_repository = order_repository
        self.user_repository = user_repository

    def create_event(self, event_create_request: EventCreate, user_uuid: UUID) -> EventDTO:
        db_place = self.place_repository.get_place_by_uuid(event_create_request.place_uuid)
        if not db_place:
            raise HTTPException(status_code=404, detail="Place not found")
        if db_place.owner_uuid != user_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to create events for this place")
        if self.is_overlapping_place_and_time(event_create_request.place_uuid, event_create_request.start_date, event_create_request.end_date):
            raise HTTPException(status_code=409, detail="Place is already booked for the given time range")
        self._validations(event_create_request, db_place)
        db_event = self.event_repository.create_event(event_create_request, user_uuid)
        return EventDTO.model_validate(db_event)

    def update_event(self, event_uuid: UUID, event_update_request: EventUpdate, user_uuid: UUID) -> EventDTO:
        logger.info(f"Updating event with UUID: {event_uuid}")

        db_event = self.event_repository.get_event_by_uuid(event_uuid)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        if db_event.owner_uuid != user_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to update this event")
        if db_event.status != EventStatus.SCHEDULED:
            raise HTTPException(status_code=409, detail="Only scheduled events can be updated")

        start_date = event_update_request.start_date or db_event.start_date
        end_date = event_update_request.end_date or db_event.end_date
        if start_date and end_date and start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")

        if event_update_request.available_number_of_tickets is not None and event_update_request.available_number_of_tickets <= 0:
            raise HTTPException(status_code=400, detail="Available number of tickets must be greater than 0")

        updated_event = self.event_repository.update_event(event_uuid, event_update_request)
        if not updated_event:
            raise HTTPException(status_code=404, detail="Event not found")
        self.notify_user_for_event_change(event_uuid, updated_event.title)
        return EventDTO.model_validate(updated_event)

    @staticmethod
    def _validations(event_create_request: EventCreate, db_place: Place):
        if event_create_request.available_number_of_tickets <= 0:
            raise HTTPException(status_code=400, detail="Available number of tickets must be greater than 0")
        if event_create_request.available_number_of_tickets > db_place.capacity:
            raise HTTPException(
                status_code=400,
                detail=f"Available number of tickets ({event_create_request.available_number_of_tickets})")
        if event_create_request.start_date > event_create_request.end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")

    def get_event_by_uuid(self, event_uuid: UUID) -> EventDTO:
        db_event = self.event_repository.get_event_by_uuid(event_uuid)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        return EventDTO.model_validate(db_event)

    def get_events_by_start_date(self, start_date: datetime) -> list[EventDTO]:
        db_events = self.event_repository.get_events_by_start_date(start_date)
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
            event_type: Optional[EventType] = None
    ) -> List[EventDTO]:
        db_events = self.event_repository.get_all_events(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type
        )
        return [EventDTO.model_validate(event) for event in db_events]

    def cancel_event(self, event_uuid: UUID, user_uuid: UUID):
        logger.info(f"Canceling event with UUID: {event_uuid}")
        db_event: Event = self.event_repository.get_event_by_uuid(event_uuid)
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        if db_event.owner_uuid != user_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this event")
        if db_event.status != EventStatus.SCHEDULED:
            raise HTTPException(status_code=409, detail="Event is not scheduled")
        result: int = self.event_repository.cancel_event(event_uuid)
        if result == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        if self.scheduler:
            for job_suffix in ("start", "end"):
                job_id = f"{event_uuid}_{job_suffix}"
                try:
                    self.scheduler.remove_job(job_id)
                except JobLookupError:
                    logger.warning(f"Scheduler job not found during cancellation: {job_id}")
        return

    def get_events_by_place_uuid(self, place_uuid: UUID) -> List[EventDTO]:
        db_events = self.event_repository.get_events_by_place_uuid(place_uuid)
        return [EventDTO.model_validate(event) for event in db_events]

    def update_events_status_with_scheduler(self):
        result = self.event_repository.update_event_statuses_by_time_to_active()
        logger.info(f"Updated {result} events to ACTIVE status based on start time")
        result = self.event_repository.update_event_statuses_by_time_to_finished()
        logger.info(f"Updated {result} events to FINISHED status based on end time")

    def is_overlapping_place_and_time(self, place_uuid: UUID, start_date: datetime, end_date: datetime) -> bool:
        overlapping_events = self.event_repository.get_overlapping_events(place_uuid, start_date, end_date)
        return overlapping_events is not None

    def notify_user_for_event_change(self, event_uuid: UUID, event_name: str):
        logger.info(f"Notifying users about event {event_uuid} change: {event_name}")
        orders = self.order_repository.get_all_orders_for_event(event_uuid)
        for order in orders:
            user = self.user_repository.get_by_uuid(order.owner_uuid)
            logger.info(f"Would notify user {user.email} about event change: {event_name}")
            EmailService.send_event_change_notification(user.email, event_uuid, event_name)
