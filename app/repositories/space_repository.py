from typing import Optional, List, cast
from uuid import UUID

from app.models.space import Space
from app.repositories.base_repository import BaseRepository


class SpaceRepository(BaseRepository):
    def create(self, name: str, description: str, owner_uuid: UUID) -> Space:
        db_obj = Space(name=name, description=description, owner_uuid=owner_uuid)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_uuid(self, space_uuid: UUID) -> Optional[Space]:
        return self.db.query(Space).filter(Space.uuid == space_uuid).first()

    def get_by_owner(self, owner_uuid: UUID) -> List[Space]:
        result = self.db.query(Space).filter(Space.owner_uuid == owner_uuid).all()
        return cast(List[Space], result)

    def get_all(self) -> List[Space]:
        result = self.db.query(Space).all()
        return cast(List[Space], result)

    def update(self, space_uuid: UUID, **kwargs) -> Optional[Space]:
        obj = self.get_by_uuid(space_uuid)
        if not obj:
            return None
        for k, v in kwargs.items():
            setattr(obj, k, v)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, space_uuid: UUID) -> int:
        obj = self.get_by_uuid(space_uuid)
        if not obj:
            return 0
        self.db.delete(obj)
        self.db.commit()
        return 1
