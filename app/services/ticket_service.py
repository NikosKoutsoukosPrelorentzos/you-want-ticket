from fastapi import HTTPException

from app.core.logger import setup_logger
from app.dtos.ticket_dto import TicketCreate, TicketDTO
from app.repositories.event_repository import EventRepository
from app.repositories.ticket_repository import TicketRepository

logger = setup_logger(__name__)


class TicketService:
    def __init__(self, ticket_repository: TicketRepository, event_repository: EventRepository):
        self.event_repository = event_repository
        self.ticket_repository = ticket_repository

    def create_ticket(self, ticket_create_request: TicketCreate) -> TicketDTO:
        logger.info(f"Attempting to create ticket for event UUID: {ticket_create_request.event_uuid}")
        event = self.event_repository.get_event_by_uuid(ticket_create_request.event_uuid)
        if not event:
            logger.error(f"Event not found: {ticket_create_request.event_uuid}")
            raise HTTPException(status_code=404, detail="Event not found")

        db_ticket = self.ticket_repository.create_ticket(ticket_create_request)
        logger.info(f"Ticket created successfully: {db_ticket.uuid}")
        return TicketDTO.model_validate(db_ticket)
