from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import update

from app.enums.event_status import EventStatus
from app.models.event import Event
from app.dtos.event_dto import EventCreate, EventUpdate
from app.enums.event_type import EventType
from app.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository):
    def create_event(self, event_create_request: EventCreate, user_uuid: UUID) -> Event:
        db_event = Event(
            owner_uuid=user_uuid,
            type=event_create_request.type,
            title=event_create_request.title,
            description=event_create_request.description,
            start_date=event_create_request.start_date,
            end_date=event_create_request.end_date,
            available_number_of_tickets=event_create_request.available_number_of_tickets,
            place_uuid=event_create_request.place_uuid
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def get_event_by_uuid(self, event_uuid: UUID) -> Optional[Event]:
        return self.db.query(Event).filter(Event.uuid == event_uuid).first()

    def get_events_by_start_date(self, start_date: datetime) -> list[type[Event]]:
        return self.db.query(Event).filter(Event.start_date == start_date).all()

    def remove_available_tickets(self, event_uuid: UUID, number_of_tickets: int) -> int:
        stmt = (
            update(Event)
            .where(Event.uuid == event_uuid)
            .where(Event.available_number_of_tickets >= number_of_tickets)
            .values(available_number_of_tickets=Event.available_number_of_tickets - number_of_tickets)
            .execution_options(synchronize_session="fetch")
        )
        result = self.db.execute(stmt)
        return result.rowcount

    def add_available_tickets(self, event_uuid: UUID, number_of_tickets: int) -> int:
        stmt = (
            update(Event)
            .where(Event.uuid == event_uuid)
            .values(available_number_of_tickets=Event.available_number_of_tickets + number_of_tickets)
            .execution_options(synchronize_session="fetch")
        )
        result = self.db.execute(stmt)
        return result.rowcount

    def get_all_events(
            self,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            event_type: Optional[EventType] = None
    ) -> List[Event]:
        query = self.db.query(Event)

        if start_date:
            query = query.filter(Event.start_date >= start_date)
        if end_date:
            query = query.filter(Event.end_date <= end_date)
        if event_type:
            query = query.filter(Event.type == event_type)


        return query.all()

    def cancel_event(self, event_uuid) -> int:
        stmt = (
            update(Event)
            .where(Event.uuid == event_uuid)
            .where(Event.status == EventStatus.SCHEDULED)
            .values(status=EventStatus.CANCELLED)
            .execution_options(synchronize_session="fetch")
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount

    def update_event(self, event_uuid: UUID, event_update_request: EventUpdate) -> Optional[Event]:
        db_event = self.get_event_by_uuid(event_uuid)
        if not db_event:
            return None

        update_data = event_update_request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_event, key, value)

        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def get_events_by_place_uuid(self, place_uuid):
        return self.db.query(Event).filter(Event.place_uuid == place_uuid).all()

    def update_event_statuses_by_time_to_active(self) -> int:
        now = datetime.utcnow()
        stmt_active = (
            update(Event)
            .where(Event.status == EventStatus.SCHEDULED)
            .where(Event.start_date <= now)
            .where(Event.end_date >= now)
            .values(status=EventStatus.ACTIVE)
            .execution_options(synchronize_session="fetch")
        )
        result_active = self.db.execute(stmt_active)
        self.db.commit()
        return result_active.rowcount

    def update_event_statuses_by_time_to_finished(self) -> int:
        now = datetime.utcnow()
        stmt_finished = (
            update(Event)
            .where(Event.status.in_([EventStatus.SCHEDULED, EventStatus.ACTIVE]))
            .where(Event.end_date <= now)
            .values(status=EventStatus.FINISHED)
            .execution_options(synchronize_session="fetch")
        )
        result_finished = self.db.execute(stmt_finished)
        self.db.commit()
        return result_finished.rowcount


    def get_overlapping_events(self, place_uuid: UUID, start_date: datetime, end_date: datetime) -> Optional[Event]:
        return self.db.query(Event).filter(
            Event.place_uuid == place_uuid,
            Event.start_date < end_date,
            Event.end_date > start_date
        ).first()
