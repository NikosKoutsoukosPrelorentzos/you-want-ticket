from enum import Enum


class OrderStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    FINALIZED = "FINALIZED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
