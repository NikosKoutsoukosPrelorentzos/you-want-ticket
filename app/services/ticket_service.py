import io
import base64
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
import qrcode
from app.core.logger import setup_logger
from app.dtos.ticket_dto import TicketCreate, TicketDTO
from app.enums.ticket_status import TicketStatus
from app.models.ticket import Ticket
from app.repositories.event_repository import EventRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.ticket_repository import TicketRepository

logger = setup_logger(__name__)


class TicketService:
    def __init__(self, ticket_repository: TicketRepository, event_repository: EventRepository, order_repository: OrderRepository):
        self.event_repository = event_repository
        self.ticket_repository = ticket_repository
        self.order_repository = order_repository

    def create_tickets(self, ticket_create_requests: List[TicketCreate]) -> List[TicketDTO]:
        if not ticket_create_requests:
            return []
        first_request = ticket_create_requests[0]
        logger.info(
            f"Attempting to create {len(ticket_create_requests)} tickets for event UUID: {first_request.event_uuid}")

        event = self.event_repository.get_event_by_uuid(first_request.event_uuid)
        if not event:
            logger.error(f"Event not found: {first_request.event_uuid}")
            raise HTTPException(status_code=404, detail="Event not found")

        created_tickets = []
        for request in ticket_create_requests:
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

    def get_tickets_by_order_uuid(self, order_uuid: UUID, user_uuid: UUID) -> List[TicketDTO]:
        db_order = self.order_repository.get_order_by_uuid(order_uuid)
        if not db_order:
            raise HTTPException(status_code=404, detail=f"Order not found: {order_uuid}")
        if db_order.owner_uuid != user_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to access this order")
        logger.info(f"Fetching tickets for order UUID: {order_uuid}")
        db_tickets = self.ticket_repository.get_tickets_by_order_uuid(order_uuid)
        return [TicketDTO.model_validate(ticket) for ticket in db_tickets]

    def cancel_ticket(self, ticket_uuid: UUID, user_uuid: UUID) -> None:
        logger.info(f"Attempting to cancel ticket: {ticket_uuid}")
        db_ticket = self.ticket_repository.get_ticket_by_uuid(ticket_uuid)
        if not db_ticket:
            logger.warning(f"Ticket not found: {ticket_uuid}")
            raise HTTPException(status_code=404, detail="Ticket not found")
        if db_ticket.owner_uuid != user_uuid:
            logger.warning(f"User {user_uuid} is not the owner of ticket {ticket_uuid}")
            raise HTTPException(status_code=403, detail="Not authorized to cancel this ticket")
        rows_affected = self.ticket_repository.cancel_ticket(ticket_uuid)
        if rows_affected == 0:
            logger.warning(f"Failed to cancel ticket {ticket_uuid}. It might not exist or is not in SCHEDULED status.")
            raise HTTPException(status_code=409, detail="Ticket could not be cancelled (invalid status or not found)")
        logger.info(f"Ticket {ticket_uuid} cancelled successfully")

    def scan_ticket(self, ticket_uuid: UUID, user_uuid: UUID) -> None:
        logger.info(f"Attempting to scan ticket: {ticket_uuid}")
        db_ticket = self.ticket_repository.get_ticket_by_uuid(ticket_uuid)
        if not db_ticket:
            logger.warning(f"Ticket not found: {ticket_uuid}")
            raise HTTPException(status_code=404, detail="Ticket not found")
        db_event = self.event_repository.get_event_by_uuid(db_ticket.event_uuid)
        if not db_event:
            logger.warning(f"Event not found: {db_ticket.event_uuid}")
            raise HTTPException(status_code=404, detail="Event not found")
        if db_event.owner_uuid != user_uuid:
            logger.warning(f"User {user_uuid} is not the owner of ticket {ticket_uuid}")
            raise HTTPException(status_code=403, detail="Not authorized to scan this ticket")

        if db_ticket.status != TicketStatus.SCHEDULED:
            logger.warning(f"Ticket {ticket_uuid} is not in SCHEDULED status")
            raise HTTPException(status_code=409, detail="Ticket is not in SCHEDULED status")

        rows_affected = self.ticket_repository.scan_ticket(ticket_uuid)
        if rows_affected == 0:
            logger.warning(f"Failed to scan ticket {ticket_uuid}. It might not exist or is not in SCHEDULED status.")
            raise HTTPException(status_code=409, detail="Ticket could not be scanned (invalid status or not found)")
        logger.info(f"Ticket {ticket_uuid} scanned successfully")

    def generate_ticket_qr_code(self, ticket_uuid) -> str:
        ticket: Optional[Ticket] = self.ticket_repository.get_ticket_by_uuid(ticket_uuid)
        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        url_to_bind: str = f"http://localhost:8000/api/v1/tickets/{ticket_uuid}/scan"
        qr = qrcode.QRCode(  # type: ignore
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(url_to_bind)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        b64 = base64.b64encode(img_buffer.read()).decode("utf-8")
        return b64
