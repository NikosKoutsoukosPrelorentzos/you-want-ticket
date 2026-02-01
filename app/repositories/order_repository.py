from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.enums.order_status import OrderStatus
from app.models.order import Order
from app.dtos.order_dto import OrderCreate


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order_create_request: OrderCreate, user_uuid: UUID) -> Order:
        db_order = Order(
            event_uuid=order_create_request.event_uuid,
            number_of_tickets=order_create_request.number_of_tickets,
            status=order_create_request.status,
            owner_uuid=user_uuid,
        )
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def get_order_by_uuid(self, order_uuid: UUID) -> Optional[Order]:
        return self.db.query(Order).filter(Order.uuid == order_uuid).first()

    def get_expired_orders(self, cutoff_time: datetime) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.created_date < cutoff_time)
            .where(Order.status == OrderStatus.IN_PROGRESS)
        )
        return self.db.scalars(stmt).all()

    def cancel_expired_order(self, order_uuid: UUID) -> int:
        stmt = (update(Order)
                .where(Order.uuid == order_uuid)
                .where(Order.status == OrderStatus.IN_PROGRESS)
                .values(status=OrderStatus.CANCELLED)
                .values(updated_date=datetime.utcnow())
                .execution_options(synchronize_session="fetch"))
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount
