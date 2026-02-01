from fastapi import APIRouter, Depends, HTTPException

from app.api import deps
from app.core.logger import setup_logger
from app.dtos.order_dto import OrderCreate, OrderDTO
from app.dtos.user_dto import UserDTO
from app.services.order_service import OrderService

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/")
def create_order(
        order_create_request: OrderCreate,
        order_service: OrderService = Depends(deps.get_order_service),
        current_user: UserDTO = Depends(deps.get_current_active_user)
) -> OrderDTO:
    try:
        logger.info(f"Creating order for user: {current_user.email}")
        return order_service.create_order(order_create_request, current_user.uuid)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
