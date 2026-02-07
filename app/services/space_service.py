from typing import List
from uuid import UUID

from fastapi import HTTPException

from app.repositories.space_repository import SpaceRepository
from app.repositories.area_repository import AreaRepository
from app.dtos.space_dto import SpaceCreate, SpaceDTO
from app.dtos.area_dto import AreaCreate, AreaDTO


class SpaceService:
    def __init__(self, space_repository: SpaceRepository, area_repository: AreaRepository):
        self.space_repository = space_repository
        self.area_repository = area_repository

    def create_space(self, space_in: SpaceCreate, owner_uuid: UUID) -> SpaceDTO:
        # create space
        space = self.space_repository.create(
            name=space_in.name,
            description=space_in.description,
            owner_uuid=owner_uuid,
        )

        # create areas transactionally: areas must reference space.uuid
        created_areas = []
        if space_in.areas:
            areas_to_create: List[AreaCreate] = []
            for area in space_in.areas:
                # ensure the area has space_uuid
                area_to_create = AreaCreate(
                    name=area.name,
                    description=area.description,
                    space_uuid=space.uuid,
                    capacity=area.capacity,
                    price_multiplier=area.price_multiplier,
                )
                areas_to_create.append(area_to_create)

            created_areas = self.area_repository.create_many(areas_to_create)

        # assemble DTO
        space_dto = SpaceDTO.model_validate(space)
        if created_areas:
            space_dto.areas = [AreaDTO.model_validate(a) for a in created_areas]
        return space_dto

    def get_space_by_uuid(self, space_uuid: UUID) -> SpaceDTO:
        space = self.space_repository.get_by_uuid(space_uuid)
        if not space:
            raise HTTPException(status_code=404, detail="Space not found")
        areas = self.area_repository.get_by_space_uuid(space_uuid)
        dto = SpaceDTO.model_validate(space)
        dto.areas = [AreaDTO.model_validate(a) for a in areas]
        return dto

    def get_spaces_for_user(self, owner_uuid: UUID) -> List[SpaceDTO]:
        spaces = self.space_repository.get_by_owner(owner_uuid)
        results: List[SpaceDTO] = []
        for s in spaces:
            dto = SpaceDTO.model_validate(s)
            areas = self.area_repository.get_by_space_uuid(s.uuid)
            dto.areas = [AreaDTO.model_validate(a) for a in areas]
            results.append(dto)
        return results

    def delete_space(self, space_uuid: UUID, owner_uuid: UUID) -> None:
        space = self.space_repository.get_by_uuid(space_uuid)
        if not space:
            raise HTTPException(status_code=404, detail="Space not found")
        if space.owner_uuid != owner_uuid:
            raise HTTPException(status_code=403, detail="Not authorized to delete this space")
        # delete areas first
        areas = self.area_repository.get_by_space_uuid(space_uuid)
        for a in areas:
            self.area_repository.delete(a.uuid)
        # delete space
        self.space_repository.delete(space_uuid)

    def get_all_spaces(self) -> List[SpaceDTO]:
        spaces = self.space_repository.get_all()
        results: List[SpaceDTO] = []
        for s in spaces:
            dto = SpaceDTO.model_validate(s)
            areas = self.area_repository.get_by_space_uuid(s.uuid)
            dto.areas = [AreaDTO.model_validate(a) for a in areas]
            results.append(dto)
        return results
