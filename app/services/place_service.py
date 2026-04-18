from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.core.logger import setup_logger
from app.dtos.place_dto import PlaceCreate, PlaceDTO, PlaceUpdate
from app.models.place import Place
from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository

logger = setup_logger(__name__)


class PlaceService:
    def __init__(self, place_repository: PlaceRepository, event_repository: EventRepository):
        self.place_repository = place_repository
        self.event_repository = event_repository

    def create_place(self, place_create: PlaceCreate, owner_uuid: UUID) -> PlaceDTO:
        if not place_create.name:
            raise HTTPException(status_code=400, detail="Place name is required")
        db_place: Place = self.place_repository.create_place(place_create, owner_uuid)
        return PlaceDTO.model_validate(db_place)

    def get_places_by_owner(self, owner_uuid: UUID) -> List[PlaceDTO]:
        db_places = self.place_repository.get_places_by_owner(owner_uuid)
        return [PlaceDTO.model_validate(p) for p in db_places]

    def get_all_places(self) -> List[PlaceDTO]:
        db_places = self.place_repository.get_all_places()
        return [PlaceDTO.model_validate(p) for p in db_places]

    def update_place(self, place_uuid: UUID, place_update: PlaceUpdate, owner_uuid: UUID) -> PlaceDTO:
        db_place = self.place_repository.get_place_by_uuid(place_uuid)
        if not db_place:
            raise HTTPException(status_code=404, detail="Place not found")
        if db_place.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to update this place")
        updated = self.place_repository.update_place(place_uuid, place_update)
        if not updated:
            raise HTTPException(status_code=404, detail="Place not found")
        return PlaceDTO.model_validate(updated)

    def delete_place(self, place_uuid: UUID, owner_uuid: UUID):
        db_place = self.place_repository.get_place_by_uuid(place_uuid)
        if not db_place:
            raise HTTPException(status_code=404, detail="Place not found")
        if db_place.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to delete this place")
        db_events = self.event_repository.get_events_by_place_uuid(place_uuid)
        if db_events:
            raise HTTPException(
                status_code=409, detail=f"Cannot delete place {place_uuid} because it has events"
            )
        result = self.place_repository.delete_place(place_uuid)
        if result == 0:
            raise HTTPException(status_code=404, detail="Place not found")
        return
