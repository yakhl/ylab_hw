from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database.db import get_db
from core.models.models import Menu, Submenu
from core.repositories.crud.crud_repository import CrudRepository
from core.schemas.full_menu_schema import Menu as MenuSchema


class FullMenuRepository(CrudRepository):
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get(self) -> list[MenuSchema]:
        query = await self.db.execute(select(Menu).options(selectinload(Menu.submenus).selectinload(Submenu.dishes)))
        return query.scalars().all()
