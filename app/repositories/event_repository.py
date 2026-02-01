from typing import Optional
from uuid import UUID

from app.models.event import Event
from app.dtos.event_dto import EventCreate


class EventRepository:
    def __init__(self, db):
        self.db = db

    def create_event(self, event_create_request: EventCreate) -> Event:
        db_event = Event(
            type=event_create_request.type,
            title=event_create_request.title,
            description=event_create_request.description,
            start_date=event_create_request.start_date,
            end_date=event_create_request.end_date,
            location=event_create_request.location,
            available_number_of_tickets=event_create_request.available_number_of_tickets
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def get_event_by_uuid(self, event_uuid: UUID) -> Optional[Event]:
        return self.db.query(Event).filter(Event.uuid == event_uuid).first()
