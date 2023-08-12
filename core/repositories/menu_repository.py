from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import distinct, func, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from ..configs.error_messages import menu_404_msg, menu_409_msg
from ..database.db import get_db
from ..models.models import Dish, Menu, Submenu
from ..schemas.menu_schemas import MenuInSchema


class MenuRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
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
            raise HTTPException(status_code=404, detail=menu_404_msg)
        return db_menu

    async def create(self, menu_data: MenuInSchema) -> Menu:
        query = await self._get_menu_query(title=menu_data.title)
        db_menu_by_title = query.first()
        if db_menu_by_title:
            raise HTTPException(status_code=409, detail=menu_409_msg)
        db_menu = Menu(**menu_data.model_dump())
        self.db.add(db_menu)
        await self.db.commit()
        await self.db.refresh(db_menu)
        return db_menu

    async def update(self, id: UUID, menu_data: MenuInSchema) -> Menu:
        query = await self._get_menu_query(id=id)
        db_menu = query.first()
        if db_menu is None:
            raise HTTPException(status_code=404, detail=menu_404_msg)
        query_by_title = await self._get_menu_query(title=menu_data.title)
        db_menu_by_title = query_by_title.first()
        if db_menu_by_title and db_menu_by_title.id != id:
            raise HTTPException(status_code=409, detail=menu_409_msg)
        updated_menu = await self.db.execute(
            update(Menu).where(Menu.id == id).values(menu_data.model_dump(exclude_unset=True)).returning(Menu)
        )
        await self.db.commit()
        return updated_menu.first()

    async def delete(self, id: UUID) -> None:
        query = await self.db.execute(select(Menu).filter_by(id=id))
        db_menu = query.scalar()
        if db_menu:
            await self.db.delete(db_menu)
            await self.db.commit()
        return
