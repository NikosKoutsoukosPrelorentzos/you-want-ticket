from datetime import datetime, timedelta

from app.core.logger import setup_logger
from app.services.event_service import EventService
from app.services.order_service import OrderService

logger = setup_logger(__name__)


class OrderCleanupService:
    def __init__(self, order_service: OrderService, event_service: EventService):
        self.order_service = order_service
        self.event_service = event_service

    def cancel_expired_orders(self) -> None:
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)

        expired_orders = self.order_service.get_expired_orders(cutoff_time)

        if not expired_orders:
            return

        logger.info(f"Found {len(expired_orders)} expired orders to cancel.")

        for order in expired_orders:
            try:
                self.order_service.cancel_expired_order(order.uuid)
                self.event_service.add_available_tickets(order.event_uuid, order.number_of_tickets)
                logger.info(f"Cancelled expired order {order.uuid} and released {order.number_of_tickets} tickets.")
            except Exception as e:
                logger.error(f"Failed to cancel order {order.uuid}: {str(e)}")
                continue
