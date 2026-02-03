from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID

from starlette.responses import JSONResponse

from app.api import deps
from app.core.logger import setup_logger
from app.dtos.order_dto import OrderCreate, OrderDTO, OrderUpdate
from app.dtos.ticket_dto import TicketDTO
from app.dtos.user_dto import UserDTO
from app.services.order_service import OrderService
from app.enums.order_status import OrderStatus

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/", response_model=OrderDTO, status_code=201)
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


@router.put("/{order_uuid}/finalize", status_code=200,
            responses={409: {"description": "Fail to finalize order"}})
def finalize_order(
        order_uuid: UUID,
        order_service: OrderService = Depends(deps.get_order_service),
        current_user: UserDTO = Depends(deps.get_current_active_user)
) -> list[TicketDTO]:
    try:
        logger.info(f"Finalizing order: {order_uuid} for user: {current_user.email}")
        return order_service.finalize_order_by_user(order_uuid, current_user.uuid)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{order_uuid}/cancel", status_code=200,
            responses={409: {"description": "Fail to cancel order"}})
def cancel_order(
        order_uuid: UUID,
        order_service: OrderService = Depends(deps.get_order_service),
        current_user: UserDTO = Depends(deps.get_current_active_user)
) -> JSONResponse:
    try:
        logger.info(f"Cancelling order: {order_uuid} for user: {current_user.email}")
        order_service.cancel_order_by_user(order_uuid, current_user.uuid)
        return JSONResponse(
            status_code=200,
            content={"message": "Order cancelled successfully"}
        )
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/all", response_model=list[OrderDTO], status_code=200)
def get_all_orders(
        start_date: Optional[datetime] = Query(None, description="Filter by creation date (>=)"),
        end_date: Optional[datetime] = Query(None, description="Filter by creation date (<=)"),
        status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
        order_service: OrderService = Depends(deps.get_order_service),
        current_user: UserDTO = Depends(deps.get_current_active_user)
) -> list[OrderDTO]:
    try:
        logger.info(
            f"Getting all orders for user: {current_user.email} with filters: start={start_date}, end={end_date}, status={status}")
        return order_service.get_all_user_orders(
            user_uuid=current_user.uuid,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
