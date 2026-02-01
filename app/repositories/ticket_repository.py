from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.dtos.ticket_dto import TicketCreate


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_ticket(self, ticket_create_request: TicketCreate) -> Ticket:
        db_ticket: Ticket = Ticket(
            event_id=ticket_create_request.event_id,
            order_id=ticket_create_request.order_id,
            status=ticket_create_request.status
        )
        self.db.add(db_ticket)
        self.db.commit()
        self.db.refresh(db_ticket)
        return db_ticket
