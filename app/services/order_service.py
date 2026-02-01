from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import UUID

from app.dtos.order_dto import OrderCreate, OrderDTO
from app.repositories.order_repository import OrderRepository
from app.services.event_service import EventService


class OrderService:
    def __init__(self, order_repository: OrderRepository, event_service: EventService):
        self.order_repository = order_repository
        self.event_service = event_service

    def create_order(self, order_create_request: OrderCreate, user_uuid: UUID) -> OrderDTO:
        db_event = self.event_service.get_event_by_uuid(order_create_request.event_uuid)
        if db_event.start_date < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Event has passed")
        if db_event.available_number_of_tickets < order_create_request.number_of_tickets:
            raise HTTPException(status_code=400, detail="Not enough tickets available")
        self.event_service.remove_available_tickets(db_event.uuid, order_create_request.number_of_tickets)
        db_order = self.order_repository.create_order(order_create_request, user_uuid)
        return OrderDTO.model_validate(db_order)

    def get_expired_orders(self, cutoff_time: datetime) -> list[OrderDTO]:
        db_orders = self.order_repository.get_expired_orders(cutoff_time)
        return [OrderDTO.model_validate(order) for order in db_orders]

    def cancel_expired_order(self, order_uuid: UUID) -> int:
        return self.order_repository.cancel_expired_order(order_uuid)
