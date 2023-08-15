from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db import get_db
from core.models.models import Dish, Submenu
from core.repositories.crud.crud_repository import CrudRepository
from core.repositories.crud.submenu_repository import SubmenuRepository
from core.schemas.dish_schemas import DishCreateSchema, DishUpdateSchema


class DishRepository(CrudRepository):
    def __init__(self, db: AsyncSession = Depends(get_db)):
        super().__init__()
        self.db = db
        self.model = Dish

        self.submenu_repo = SubmenuRepository(self.db)

    async def _get_dish_query(self, menu_id: UUID, **kwargs) -> Result:
        return await self.db.execute(
            select(Dish.id, Dish.title, Dish.description, Dish.price, Dish.submenu_id)
            .filter_by(**kwargs)
            .join(Submenu, Submenu.menu_id == menu_id)
            .group_by(Dish.id)
        )

    async def get_all(self, menu_id: UUID, submenu_id: UUID) -> list[Dish]:
        query = await self._get_dish_query(menu_id=menu_id, submenu_id=submenu_id)
        return query.all()

    async def get(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> Dish:
        query = await self._get_dish_query(menu_id=menu_id, submenu_id=submenu_id, id=dish_id)
        db_dish = query.first()
        if db_dish is None:
            raise HTTPException(status_code=404, detail=self.dish_404_msg)
        return db_dish

    async def create(self, menu_id: UUID, submenu_id: UUID, dish_data: DishCreateSchema) -> Dish:
        db_submenu = await self.submenu_repo._get_submenu_query(menu_id=menu_id, id=submenu_id)
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=self.submenu_404_msg)
        dish_query_by_id = await self.db.execute(select(Dish.id).filter_by(id=dish_data.id))
        db_dish_by_id = dish_query_by_id.first()
        if db_dish_by_id:
            raise HTTPException(status_code=409, detail=self.dish_409_id_msg)
        query = await self._get_dish_query(menu_id=menu_id, submenu_id=submenu_id, title=dish_data.title)
        db_dish_by_title = query.first()
        if db_dish_by_title:
            raise HTTPException(status_code=409, detail=self.dish_409_title_msg)
        db_dish = Dish(submenu_id=submenu_id, **dish_data.model_dump())
        self.db.add(db_dish)
        await self.db.commit()
        await self.db.refresh(db_dish)
        return db_dish

    async def update(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data: DishUpdateSchema) -> Dish:
        query = await self._get_dish_query(menu_id=menu_id, submenu_id=submenu_id, id=dish_id)
        db_dish = query.first()
        if db_dish is None:
            raise HTTPException(status_code=404, detail=self.dish_404_msg)
        query_by_title = await self._get_dish_query(menu_id=menu_id, submenu_id=submenu_id, title=dish_data.title)
        db_dish_by_title = query_by_title.first()
        if db_dish_by_title and str(db_dish_by_title.id) != str(dish_id):
            raise HTTPException(status_code=409, detail=self.dish_409_title_msg)
        update_query = await self.db.execute(
            update(Dish).where(Dish.id == dish_id).values(dish_data.model_dump(exclude_unset=True)).returning(Dish)
        )
        await self.db.commit()
        return update_query.first()

    async def delete(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> dict:
        query = await self.db.execute(
            select(Dish)
            .filter_by(submenu_id=submenu_id, id=dish_id)
            .outerjoin(Submenu, Submenu.menu_id == menu_id)
            .group_by(Dish.id)
        )
        db_dish = query.scalar()
        if db_dish:
            await self.db.delete(db_dish)
            await self.db.commit()
        return {'status': True, 'message': self.dish_200_deleted_msg}

    async def get_all_ids(self, submenu_id: UUID) -> list[UUID]:
        query = await self.db.execute(select(Dish.id).filter_by(submenu_id=submenu_id))
        return query.scalars().all()
