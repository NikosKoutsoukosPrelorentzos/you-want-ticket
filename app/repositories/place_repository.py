from typing import Optional
from uuid import UUID

from app.models.place import Place
from app.dtos.place_dto import PlaceCreate, PlaceUpdate
from app.repositories.base_repository import BaseRepository


class PlaceRepository(BaseRepository):
    def create_place(self, place_create: PlaceCreate, owner_uuid: UUID) -> Place:
        db_place = Place(
            name=place_create.name,
            address=place_create.address,
            capacity=place_create.capacity,
            owner_uuid=owner_uuid
        )
        self.db.add(db_place)
        self.db.commit()
        self.db.refresh(db_place)
        return db_place

    def get_place_by_uuid(self, place_uuid: UUID) -> Optional[Place]:
        return self.db.query(Place).filter(Place.uuid == place_uuid).first()

    def get_places_by_owner(self, owner_uuid: UUID) -> list[Place]:
        return self.db.query(Place).filter(Place.owner_uuid == owner_uuid).all()

    def update_place(self, place_uuid: UUID, place_update: PlaceUpdate) -> Optional[Place]:
        db_place = self.get_place_by_uuid(place_uuid)
        if not db_place:
            return None
        update_data = place_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_place, key, value)
        self.db.commit()
        self.db.refresh(db_place)
        return db_place

    def delete_place(self, place_uuid: UUID) -> int:
        place = self.get_place_by_uuid(place_uuid)
        if not place:
            return 0
        self.db.delete(place)
        self.db.commit()
        return 1
