from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.event import Event
from app.dtos.event_dto import EventCreate


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_event(self, event_create_request: EventCreate, user_uuid: UUID) -> Event:
        db_event = Event(
            owner_uuid=user_uuid,
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

    def get_events_by_start_date(self, start_date: datetime) -> list[type[Event]]:
        return self.db.query(Event).filter(Event.start_date == start_date).all()

    def get_events_by_location(self, location: str) -> list[type[Event]]:
        return self.db.query(Event).filter(Event.location == location).all()

    def remove_available_tickets(self, event_uuid: UUID, number_of_tickets: int) -> int:
        stmt = (
            update(Event)
            .where(Event.uuid == event_uuid)
            .where(Event.available_number_of_tickets >= number_of_tickets)
            .values(available_number_of_tickets=Event.available_number_of_tickets - number_of_tickets)
            .execution_options(synchronize_session="fetch")
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount

    def add_available_tickets(self, event_uuid: UUID, number_of_tickets: int) -> int:
        stmt = (
            update(Event)
            .where(Event.uuid == event_uuid)
            .values(available_number_of_tickets=Event.available_number_of_tickets + number_of_tickets)
            .execution_options(synchronize_session="fetch")
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount
