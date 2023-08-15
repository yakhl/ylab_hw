from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database.db import get_db
from ..models.models import Menu, Submenu
from ..schemas.full_menu_schema import Menu as MenuSchema
from .crud_repository import CrudRepository


class FullMenuRepository(CrudRepository):
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get(self) -> list[MenuSchema]:
        query = await self.db.execute(select(Menu).options(selectinload(Menu.submenus).selectinload(Submenu.dishes)))
        return query.scalars().all()
