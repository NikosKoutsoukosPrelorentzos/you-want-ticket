from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy import UUID

from app.core.logger import setup_logger
from app.dtos.order_dto import OrderCreate, OrderDTO
from app.dtos.ticket_dto import TicketCreate, TicketDTO
from app.dtos.user_dto import UserDTO
from app.enums.ticket_status import TicketStatus
from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.services.email_service import EmailService
from app.services.event_service import EventService
from app.enums.order_status import OrderStatus
from app.services.ticket_service import TicketService

logger = setup_logger(__name__)


class OrderService:
    def __init__(self, order_repository: OrderRepository, event_service: EventService, ticket_service: TicketService):
        self.ticket_service = ticket_service
        self.order_repository = order_repository
        self.event_service = event_service

    def create_order(self, order_create_request: OrderCreate, user_uuid: UUID) -> OrderDTO:
        db_event = self.event_service.get_event_by_uuid(order_create_request.event_uuid)
        if db_event.start_date < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Event has passed")
        if db_event.available_number_of_tickets < order_create_request.number_of_tickets:
            raise HTTPException(status_code=400, detail="Not enough tickets available")
        try:
            self.event_service.remove_available_tickets(db_event.uuid, order_create_request.number_of_tickets)
            db_order = self.order_repository.create_order(order_create_request, user_uuid)
            self.order_repository.commit()
            return OrderDTO.model_validate(db_order)
        except Exception as e:
            logger.error(e)
            self.order_repository.rollback()
            logger.info("Rolling back transaction")
            raise e

    def get_expired_orders(self, cutoff_time: datetime) -> list[OrderDTO]:
        db_orders = self.order_repository.get_expired_orders(cutoff_time)
        return [OrderDTO.model_validate(order) for order in db_orders]

    def cancel_expired_order(self, order_uuid: UUID) -> int:
        result: int = self.order_repository.cancel_expired_order(order_uuid)
        if result == 0:
            raise HTTPException(status_code=409, detail=f"Fail to cancel order: {order_uuid}")
        return result

    def finalize_order_by_user(self, order_uuid: UUID, user: UserDTO) -> list[TicketDTO]:
        db_order = self.order_repository.get_order_by_uuid(order_uuid)
        if not db_order:
            raise HTTPException(status_code=404, detail=f"Order not found: {order_uuid}")
        if db_order.owner_uuid != user.uuid:
            raise HTTPException(status_code=403, detail="Not authorized to finalize this order")
        if db_order.status != OrderStatus.IN_PROGRESS:
            raise HTTPException(status_code=409, detail=f"Order is not in progress: {order_uuid}")
        try:
            result: int = self.order_repository.finalize_order_by_user(order_uuid, user.uuid)
            if result == 0:
                raise HTTPException(status_code=409, detail=f"Fail to finalize order: {order_uuid}")
            ticket_requests = [
                TicketCreate(
                    event_uuid=db_order.event_uuid,
                    order_uuid=db_order.uuid,
                    owner_uuid=user.uuid,
                    status=TicketStatus.SCHEDULED
                )
                for _ in range(db_order.number_of_tickets)
            ]
            tickets: list[TicketDTO] = self.ticket_service.create_tickets(ticket_requests)
            for ticket in tickets:
                ticket.qr_code = self.ticket_service.generate_ticket_qr_code(ticket.uuid)
            EmailService.send_email(user.email, tickets)
            self.order_repository.commit()
            return tickets
        except Exception as e:
            logger.error(e)
            self.order_repository.rollback()
            logger.info(f"Rolling back transaction for order: {order_uuid}")
            raise e

    def cancel_order_by_user(self, order_uuid: UUID, user_uuid: UUID) -> int:
        db_order =self.get_and_validate_order_ownership(order_uuid, user_uuid)
        if db_order.status != OrderStatus.IN_PROGRESS:
            raise HTTPException(status_code=409, detail=f"Order is not in progress: {order_uuid}")
        try:
            tickets = self.ticket_service.get_tickets_by_order_uuid(order_uuid, user_uuid)
            for ticket in tickets:
                self.ticket_service.cancel_ticket(ticket.uuid, user_uuid)
            result: int = self.order_repository.cancel_order_by_user(order_uuid, user_uuid)
            if result == 0:
                raise HTTPException(status_code=409, detail=f"Fail to cancel order: {order_uuid}")
            self.event_service.add_available_tickets(db_order.event_uuid, db_order.number_of_tickets)
            self.order_repository.commit()
            return result
        except Exception as e:
            logger.error(e)
            self.order_repository.rollback()
            logger.info(f"Rolling back transaction for order: {order_uuid}")
            raise e

    def get_and_validate_order_ownership(self, order_uuid: UUID, user_uuid: UUID) -> Order:
        db_order = self.order_repository.get_order_by_uuid(order_uuid)
        if not db_order:
            raise HTTPException(status_code=404, detail=f"Order not found: {order_uuid}")
        if db_order.owner_uuid != user_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to access this order")
        return db_order

    def get_all_user_orders(
            self,
            user_uuid: UUID,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            status: Optional[OrderStatus] = None
    ) -> List[OrderDTO]:
        db_orders = self.order_repository.get_all_user_order(
            user_uuid=user_uuid,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        return [OrderDTO.model_validate(order) for order in db_orders]
