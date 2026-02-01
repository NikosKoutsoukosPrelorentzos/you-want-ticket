from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import UUID

from app.dtos.event_dto import EventCreate, EventDTO
from app.repositories.event_repository import EventRepository


class EventService:
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository

    def create_event(self, event_create_request: EventCreate, user_uuid: UUID) -> EventDTO:
        self._validations(event_create_request)
        db_event = self.event_repository.create_event(event_create_request, user_uuid)
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
