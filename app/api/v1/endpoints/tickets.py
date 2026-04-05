from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import StreamingResponse
import io
import base64

from app.api import deps
from app.api.deps import get_ticket_service
from app.core.logger import setup_logger
from app.core.role_checker import organizer_checker
from app.dtos.user_dto import UserDTO

router = APIRouter()
logger = setup_logger(__name__)


@router.put("/{ticket_uuid}/scan", status_code=200)
def scan_ticket(
        ticket_uuid: str,
        current_user: UserDTO = Depends(organizer_checker),
        ticket_service=Depends(get_ticket_service)
):
    try:
        logger.info(f"Scanning ticket: {ticket_uuid} by organizer: {current_user.email}")
        ticket_service.scan_ticket(ticket_uuid)
        return {"message": "Ticket scanned successfully"}
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(f"Error scanning ticket: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{ticket_uuid}/qr", status_code=200)
def get_ticket_qr_code(
        ticket_uuid: str,
        current_user: UserDTO = Depends(deps.get_current_active_user),
        ticket_service=Depends(get_ticket_service)
):
    try:
        logger.info(f"Generating QR code for ticket: {ticket_uuid} by organizer: {current_user.email}")
        b64 = ticket_service.generate_ticket_qr_code(ticket_uuid)
        img_bytes = base64.b64decode(b64)
        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(f"Error generating QR code for ticket: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/all/{order_uuid}", status_code=200)
def get_tickets_by_order(
        order_uuid: str,
        current_user: UserDTO = Depends(deps.get_current_active_user),
        ticket_service=Depends(get_ticket_service)
):
    try:
        logger.info(f"Fetching tickets for order: {order_uuid} by user: {current_user.email}")
        return ticket_service.get_tickets_by_order_uuid(order_uuid, current_user.uuid)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(f"Error fetching tickets for order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")