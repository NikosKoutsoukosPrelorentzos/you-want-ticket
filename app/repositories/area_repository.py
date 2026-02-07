from typing import Optional, List, cast
from uuid import UUID

from app.models.area import Area
from app.repositories.base_repository import BaseRepository


class AreaRepository(BaseRepository):
    def create(self, area_in) -> Area:
        db_obj = Area(
            name=area_in.name,
            description=area_in.description,
            space_uuid=area_in.space_uuid,
            capacity=area_in.capacity,
            price_multiplier=area_in.price_multiplier,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create_many(self, areas) -> List[Area]:
        objs = []
        for a in areas:
            obj = Area(
                name=a.name,
                description=a.description,
                space_uuid=a.space_uuid,
                capacity=a.capacity,
                price_multiplier=a.price_multiplier,
            )
            self.db.add(obj)
            objs.append(obj)
        self.db.commit()
        for obj in objs:
            self.db.refresh(obj)
        return objs

    def get_by_uuid(self, area_uuid: UUID) -> Optional[Area]:
        return self.db.query(Area).filter(Area.uuid == area_uuid).first()

    def get_by_space_uuid(self, space_uuid: UUID) -> List[Area]:
        result = self.db.query(Area).filter(Area.space_uuid == space_uuid).all()
        return cast(List[Area], result)

    def delete(self, area_uuid: UUID) -> int:
        obj = self.db.query(Area).filter(Area.uuid == area_uuid).first()
        if not obj:
            return 0
        self.db.delete(obj)
        self.db.commit()
        return 1
