from typing import Optional
from uuid import UUID

from app.models.order import Order
from app.dtos.order_dto import OrderCreate


class OrderRepository:
    def __init__(self, db):
        self.db = db

    def create_order(self, order_create_request: OrderCreate) -> Order:
        db_order = Order(
            event_id=order_create_request.event_id,
            number_of_tickets=order_create_request.number_of_tickets,
            status=order_create_request.status,
            owner_id=order_create_request.owner_id
        )
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def get_order_by_uuid(self, order_uuid: UUID) -> Optional[Order]:
        return self.db.query(Order).filter(Order.uuid == order_uuid).first()
