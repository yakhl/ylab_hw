from uuid import UUID

from fastapi import Depends

from core.models.models import Menu
from core.repositories.cache_repository import CacheRepository
from core.repositories.menu_repository import MenuRepository
from core.schemas.menu_schemas import MenuCreateSchema, MenuUpdateSchema


class MenuService:
    def __init__(self, cache_repository: CacheRepository = Depends(), menu_repository: MenuRepository = Depends()):
        self.menu_repository = menu_repository
        self.cache_repository = cache_repository

    async def get_all(self) -> list[Menu]:
        cached_menus = await self.cache_repository.get_all_menus()
        if cached_menus:
            return cached_menus
        db_menus = await self.menu_repository.get_all()
        await self.cache_repository.set_all_menus(db_menus)
        return db_menus

    async def get(self, id: UUID) -> Menu:
        cached_menu = await self.cache_repository.get_menu(id)
        if cached_menu:
            return cached_menu
        db_menu = await self.menu_repository.get(id=id)
        await self.cache_repository.set_menu(db_menu.id, db_menu)
        return db_menu

    async def create(self, menu_data: MenuCreateSchema) -> Menu:
        db_menu = await self.menu_repository.create(menu_data=menu_data)
        await self.cache_repository.create_menu(db_menu)
        return db_menu

    async def update(self, id: UUID, menu_data: MenuUpdateSchema) -> Menu:
        db_menu = await self.menu_repository.update(id=id, menu_data=menu_data)
        await self.cache_repository.update_menu(db_menu)
        return db_menu

    async def delete(self, id: UUID) -> dict:
        deleted = await self.menu_repository.delete(id=id)
        await self.cache_repository.delete_menu(menu_id=id)
        return deleted

    async def get_all_ids(self) -> list[UUID]:
        return await self.menu_repository.get_all_ids()
