from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update

from app.enums.order_status import OrderStatus
from app.models.order import Order
from app.dtos.order_dto import OrderCreate
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    def create_order(self, order_create_request: OrderCreate, user_uuid: UUID) -> Order:
        db_order = Order(
            event_uuid=order_create_request.event_uuid,
            number_of_tickets=order_create_request.number_of_tickets,
            status=order_create_request.status,
            owner_uuid=user_uuid,
        )
        self.db.add(db_order)
        self.db.flush()
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
        return result.rowcount

    def finalize_order_by_user(self, order_uuid: UUID, user_uuid: UUID) -> int:
        stmt = (update(Order)
                .where(Order.uuid == order_uuid)
                .where(Order.owner_uuid == user_uuid)
                .where(Order.status == OrderStatus.IN_PROGRESS)
                .values(status=OrderStatus.FINALIZED)
                .values(updated_date=datetime.utcnow())
                .execution_options(synchronize_session="fetch")
                )
        result = self.db.execute(stmt)
        return result.rowcount

    def cancel_order_by_user(self, order_uuid: UUID, user_uuid: UUID):
        stmt = (update(Order)
                .where(Order.uuid == order_uuid)
                .where(Order.owner_uuid == user_uuid)
                .values(status=OrderStatus.CANCELLED)
                .values(updated_date=datetime.utcnow())
                .execution_options(synchronize_session="fetch")
                )
        result = self.db.execute(stmt)
        return result.rowcount

    def get_all_user_order(
        self, 
        user_uuid: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        stmt = select(Order).where(Order.owner_uuid == user_uuid)
        
        if start_date:
            stmt = stmt.where(Order.created_date >= start_date)
        if end_date:
            stmt = stmt.where(Order.created_date <= end_date)
        if status:
            stmt = stmt.where(Order.status == status)

        return self.db.scalars(stmt).all()
