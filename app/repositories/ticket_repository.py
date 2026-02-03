from sqlalchemy import update
from sqlalchemy.orm import Session
from uuid import UUID

from app.enums.ticket_status import TicketStatus
from app.models.ticket import Ticket
from app.dtos.ticket_dto import TicketCreate


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_ticket(self, ticket_create_request: TicketCreate) -> Ticket:
        db_ticket: Ticket = Ticket(
            event_uuid=ticket_create_request.event_uuid,
            order_uuid=ticket_create_request.order_uuid,
            status=ticket_create_request.status
        )
        self.db.add(db_ticket)
        self.db.commit()
        self.db.refresh(db_ticket)
        return db_ticket

    def get_ticket_by_uuid(self, ticket_uuid: UUID) -> Ticket:
        return self.db.query(Ticket).filter(Ticket.uuid == ticket_uuid).first()

    def get_tickets_by_order_uuid(self, order_uuid: UUID) -> list[Ticket]:
        return self.db.query(Ticket).filter(Ticket.order_uuid == order_uuid).all()

    def cancel_ticket(self, ticket_uuid: UUID) -> int:
        stmt = (update(Ticket)
                .where(Ticket.uuid == ticket_uuid)
                .where(Ticket.status == TicketStatus.SCHEDULED)
                .values(status=TicketStatus.CANCELLED)
                )
        return self.db.execute(stmt).rowcount

    def finalize_ticket(self, ticket_uuid: UUID) -> int:
        stmt = (update(Ticket)
                .where(Ticket.uuid == ticket_uuid)
                .where(Ticket.status == TicketStatus.SCHEDULED)
                .values(status=TicketStatus.FINALIZED)
                )
        return self.db.execute(stmt).rowcount
