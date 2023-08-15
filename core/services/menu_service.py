import json
from uuid import UUID

from fastapi import Depends

from ..configs.cache_tags import all_menus_tag
from ..configs.error_messages import menu_200_deleted_msg
from ..models.models import Menu
from ..repositories.cache_repository import CacheRepository
from ..repositories.menu_repository import MenuRepository
from ..schemas.menu_schemas import MenuCreateSchema, MenuUpdateSchema
from .main_service import MainService


class MenuService(MainService):
    def __init__(self, cache_repository: CacheRepository = Depends(), menu_repository: MenuRepository = Depends()):
        self.menu_repository = menu_repository
        self.cache_repository = cache_repository

    async def get_all(self) -> list[Menu]:
        cached_menus = await self.cache_repository.get(all_menus_tag)
        if cached_menus is not None:
            return json.loads(cached_menus)
        db_menus = await self.menu_repository.get_all()
        await self.cache_repository.set(all_menus_tag, db_menus)
        return db_menus

    async def get(self, id: UUID) -> Menu:
        cached_menu = await self.cache_repository.get(id)
        if cached_menu is not None:
            return json.loads(cached_menu)
        db_menu = await self.menu_repository.get(id=id)
        await self.cache_repository.set(db_menu.id, db_menu)
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
        await self.menu_repository.delete(id=id)
        await self.cache_repository.delete_menu(menu_id=id)
        return {'status': True, 'message': menu_200_deleted_msg}

    async def get_all_ids(self) -> list[UUID]:
        return await self.menu_repository.get_all_ids()
