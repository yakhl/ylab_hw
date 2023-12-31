from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import distinct, func, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db import get_db
from core.models.models import Dish, Submenu
from core.repositories.crud.crud_repository import CrudRepository
from core.repositories.crud.menu_repository import MenuRepository
from core.schemas.submenu_schemas import SubmenuCreateSchema, SubmenuUpdateSchema


class SubmenuRepository(CrudRepository):
    def __init__(self, db: AsyncSession = Depends(get_db)):
        super().__init__()
        self.db = db
        self.model = Submenu
        self.menu_repo = MenuRepository(self.db)

    async def _get_submenu_query(self, **kwargs) -> Result:
        query = await self.db.execute(
            select(
                Submenu.id,
                Submenu.title,
                Submenu.description,
                Submenu.menu_id,
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .filter_by(**kwargs)
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .group_by(Submenu.id)
        )
        return query

    async def get_all(self, menu_id: UUID) -> list[Submenu]:
        query = await self._get_submenu_query(menu_id=menu_id)
        return query.all()

    async def get(self, menu_id: UUID, submenu_id: UUID) -> Submenu:
        query = await self._get_submenu_query(menu_id=menu_id, id=submenu_id)
        db_submenu = query.first()
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=self.submenu_404_msg)
        return db_submenu

    async def create(self, menu_id: UUID, submenu_data: SubmenuCreateSchema) -> Submenu:
        menu_query = await self.menu_repo._get_menu_query(id=menu_id)
        if menu_query.first() is None:
            raise HTTPException(status_code=404, detail=self.menu_404_msg)
        query_by_id = await self.db.execute(
            select(
                Submenu.id,
            ).filter_by(id=submenu_data.id)
        )
        if query_by_id.first():
            raise HTTPException(status_code=409, detail=self.submenu_409_id_msg)
        query_by_title = await self._get_submenu_query(menu_id=menu_id, title=submenu_data.title)
        if query_by_title.first():
            raise HTTPException(status_code=409, detail=self.submenu_409_title_msg)
        db_submenu = Submenu(menu_id=menu_id, **submenu_data.model_dump())
        self.db.add(db_submenu)
        await self.db.commit()
        await self.db.refresh(db_submenu)
        return db_submenu

    async def update(self, menu_id: UUID, submenu_id: UUID, submenu_data: SubmenuUpdateSchema) -> Submenu:
        query = await self._get_submenu_query(menu_id=menu_id, id=submenu_id)
        db_submenu = query.first()
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=self.submenu_404_msg)
        query_by_title = await self._get_submenu_query(menu_id=menu_id, title=submenu_data.title)
        db_submenu_by_title = query_by_title.first()
        if db_submenu_by_title and str(db_submenu_by_title.id) != str(submenu_id):
            raise HTTPException(status_code=409, detail=self.submenu_409_title_msg)
        updated_submenu = await self.db.execute(
            update(Submenu)
            .where(Submenu.id == submenu_id)
            .values(submenu_data.model_dump(exclude_unset=True))
            .returning(Submenu)
        )
        await self.db.commit()
        return updated_submenu.first()

    async def delete(self, menu_id: UUID, submenu_id: UUID) -> dict:
        query = await self.db.execute(select(Submenu).filter_by(id=submenu_id, menu_id=menu_id))
        db_submenu = query.scalar()
        if db_submenu:
            await self.db.delete(db_submenu)
            await self.db.commit()
        return {'status': True, 'message': self.submenu_200_deleted_msg}

    async def get_all_ids(self, menu_id: UUID) -> list[UUID]:
        query = await self.db.execute(select(Submenu.id).filter_by(menu_id=menu_id))
        return query.scalars().all()
