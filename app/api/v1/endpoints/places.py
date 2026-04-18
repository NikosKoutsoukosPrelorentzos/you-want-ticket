from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from app.api import deps
from app.core.logger import setup_logger
from app.core.role_checker import organizer_checker
from app.dtos.place_dto import PlaceDTO, PlaceCreate, PlaceUpdate
from app.dtos.user_dto import UserDTO
from app.services.place_service import PlaceService

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/", response_model=PlaceDTO)
def create_place(
        place_create_request: PlaceCreate,
        place_service: PlaceService = Depends(deps.get_place_service),
        current_user: UserDTO = Depends(organizer_checker),
) -> PlaceDTO:
    try:
        logger.info(f"Creating place for user: {current_user.email}")
        return place_service.create_place(place_create_request, current_user.uuid)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/all", response_model=List[PlaceDTO])
def get_all_places(
        place_service: PlaceService = Depends(deps.get_place_service),
        current_user: UserDTO = Depends(deps.get_current_active_user)
) -> List[PlaceDTO]:
    try:
        logger.info(f"Getting all places for user: {current_user.email}")
        return place_service.get_all_places()
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/owned", response_model=List[PlaceDTO])
def get_owned_places(
        place_service: PlaceService = Depends(deps.get_place_service),
        current_user: UserDTO = Depends(organizer_checker)
) -> List[PlaceDTO]:
    try:
        logger.info(f"Getting places owned by user: {current_user.email}")
        return place_service.get_places_by_owner(current_user.uuid)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{place_uuid}/update", response_model=PlaceDTO)
def update_place(
        place_uuid: UUID,
        place_update_request: PlaceUpdate,
        place_service: PlaceService = Depends(deps.get_place_service),
        current_user: UserDTO = Depends(organizer_checker)
) -> PlaceDTO:
    try:
        logger.info(f"Updating place: {place_uuid} for user: {current_user.email}")
        return place_service.update_place(place_uuid, place_update_request, current_user.uuid)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{place_uuid}/delete")
def delete_place(
        place_uuid: UUID,
        place_service: PlaceService = Depends(deps.get_place_service),
        current_user: UserDTO = Depends(organizer_checker)
) -> JSONResponse:
    try:
        logger.info(f"Deleting place: {place_uuid} for user: {current_user.email}")
        place_service.delete_place(place_uuid, current_user.uuid)
        return JSONResponse(status_code=200, content={"message": "Place deleted successfully"})
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
