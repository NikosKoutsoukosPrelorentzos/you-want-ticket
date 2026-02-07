from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_space_service, get_current_active_user
from app.dtos.space_dto import SpaceCreate, SpaceDTO
from app.dtos.user_dto import UserDTO

router = APIRouter()


@router.post("/", response_model=SpaceDTO, status_code=201)
def create_space(
    space_create_request: SpaceCreate,
    space_service=Depends(get_space_service),
    current_user: UserDTO = Depends(get_current_active_user),
) -> SpaceDTO:
    try:
        return space_service.create_space(space_create_request, current_user.uuid)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{space_uuid}", response_model=SpaceDTO)
def get_space(
    space_uuid: UUID,
    space_service=Depends(get_space_service),
    current_user: UserDTO = Depends(get_current_active_user),
) -> SpaceDTO:
    try:
        return space_service.get_space_by_uuid(space_uuid)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[SpaceDTO])
def list_spaces(
    space_service=Depends(get_space_service),
    current_user: UserDTO = Depends(get_current_active_user),
) -> List[SpaceDTO]:
    try:
        return space_service.get_spaces_for_user(current_user.uuid)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{space_uuid}", status_code=204)
def delete_space(
    space_uuid: UUID,
    space_service=Depends(get_space_service),
    current_user: UserDTO = Depends(get_current_active_user),
):
    try:
        space_service.delete_space(space_uuid, current_user.uuid)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
