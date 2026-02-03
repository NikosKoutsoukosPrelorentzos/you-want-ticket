from typing import List
from uuid import UUID

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

    def create_tickets(self, ticket_create_requests: List[TicketCreate]) -> List[TicketDTO]:
        if not ticket_create_requests:
            return []
        first_request = ticket_create_requests[0]
        logger.info(f"Attempting to create {len(ticket_create_requests)} tickets for event UUID: {first_request.event_uuid}")
        
        event = self.event_repository.get_event_by_uuid(first_request.event_uuid)
        if not event:
            logger.error(f"Event not found: {first_request.event_uuid}")
            raise HTTPException(status_code=404, detail="Event not found")

        created_tickets = []
        for request in ticket_create_requests:
             # We could optimize this with a bulk insert in the repository later
            db_ticket = self.ticket_repository.create_ticket(request)
            created_tickets.append(TicketDTO.model_validate(db_ticket))
            
        logger.info(f"Successfully created {len(created_tickets)} tickets")
        return created_tickets

    def get_ticket_by_uuid(self, ticket_uuid: UUID) -> TicketDTO:
        logger.info(f"Fetching ticket with UUID: {ticket_uuid}")
        db_ticket = self.ticket_repository.get_ticket_by_uuid(ticket_uuid)
        if not db_ticket:
            logger.warning(f"Ticket not found: {ticket_uuid}")
            raise HTTPException(status_code=404, detail="Ticket not found")
        return TicketDTO.model_validate(db_ticket)

    def get_tickets_by_order_uuid(self, order_uuid: UUID) -> List[TicketDTO]:
        logger.info(f"Fetching tickets for order UUID: {order_uuid}")
        db_tickets = self.ticket_repository.get_tickets_by_order_uuid(order_uuid)
        return [TicketDTO.model_validate(ticket) for ticket in db_tickets]

    def cancel_ticket(self, ticket_uuid: UUID) -> None:
        logger.info(f"Attempting to cancel ticket: {ticket_uuid}")
        rows_affected = self.ticket_repository.cancel_ticket(ticket_uuid)
        if rows_affected == 0:
            logger.warning(f"Failed to cancel ticket {ticket_uuid}. It might not exist or is not in SCHEDULED status.")
            raise HTTPException(status_code=409, detail="Ticket could not be cancelled (invalid status or not found)")
        logger.info(f"Ticket {ticket_uuid} cancelled successfully")

    def finalize_ticket(self, ticket_uuid: UUID) -> None:
        logger.info(f"Attempting to finalize ticket: {ticket_uuid}")
        rows_affected = self.ticket_repository.finalize_ticket(ticket_uuid)
        if rows_affected == 0:
            logger.warning(f"Failed to finalize ticket {ticket_uuid}. It might not exist or is not in SCHEDULED status.")
            raise HTTPException(status_code=409, detail="Ticket could not be finalized (invalid status or not found)")
        logger.info(f"Ticket {ticket_uuid} finalized successfully")
