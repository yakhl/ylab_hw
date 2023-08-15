from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import distinct, func, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db import get_db
from core.models.models import Dish, Menu, Submenu
from core.repositories.crud.crud_repository import CrudRepository
from core.schemas.menu_schemas import MenuCreateSchema, MenuUpdateSchema


class MenuRepository(CrudRepository):
    def __init__(self, db: AsyncSession = Depends(get_db)):
        super().__init__()
        self.db = db
        self.model = Menu

    async def _get_menu_query(self, **kwargs) -> Result:
        query = await self.db.execute(
            select(
                Menu.id,
                Menu.title,
                Menu.description,
                func.count(distinct(Submenu.id)).label('submenus_count'),
                func.count(distinct(Dish.id)).label('dishes_count'),
            )
            .filter_by(**kwargs)
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .group_by(Menu.id)
        )
        return query

    async def get_all(self) -> list[Menu]:
        query = await self._get_menu_query()
        return query.all()

    async def get(self, id: UUID) -> Menu:
        query = await self._get_menu_query(id=id)
        db_menu = query.first()
        if db_menu is None:
            raise HTTPException(status_code=404, detail=self.menu_404_msg)
        return db_menu

    async def create(self, menu_data: MenuCreateSchema) -> Menu:
        query_by_id = await self.db.execute(select(Menu.id).filter_by(id=menu_data.id))
        if query_by_id.first():
            raise HTTPException(status_code=409, detail=self.menu_409_id_msg)
        query = await self._get_menu_query(title=menu_data.title)
        db_menu_by_title = query.first()
        if db_menu_by_title:
            raise HTTPException(status_code=409, detail=self.menu_409_title_msg)
        db_menu = Menu(**menu_data.model_dump())
        self.db.add(db_menu)
        await self.db.commit()
        await self.db.refresh(db_menu)
        return db_menu

    async def update(self, id: UUID, menu_data: MenuUpdateSchema) -> Menu:
        query = await self._get_menu_query(id=id)
        db_menu = query.first()
        if db_menu is None:
            raise HTTPException(status_code=404, detail=self.menu_404_msg)
        query_by_title = await self._get_menu_query(title=menu_data.title)
        db_menu_by_title = query_by_title.first()
        if db_menu_by_title and str(db_menu_by_title.id) != str(id):
            raise HTTPException(status_code=409, detail=self.menu_409_title_msg)
        updated_menu = await self.db.execute(
            update(Menu).where(Menu.id == id).values(menu_data.model_dump(exclude_unset=True)).returning(Menu)
        )
        await self.db.commit()
        return updated_menu.first()

    async def delete(self, id: UUID) -> dict:
        query = await self.db.execute(select(Menu).filter_by(id=id))
        db_menu = query.scalar()
        if db_menu:
            await self.db.delete(db_menu)
            await self.db.commit()
        return {'status': True, 'message': self.menu_200_deleted_msg}

    async def get_all_ids(self) -> list[UUID]:
        query = await self.db.execute(select(Menu.id))
        return query.scalars().all()
