from uuid import UUID

from fastapi import Depends

from core.models.models import Submenu
from core.repositories.cache.submenu_repository import SubmenuCacheRepository
from core.repositories.crud.submenu_repository import SubmenuRepository
from core.schemas.submenu_schemas import SubmenuCreateSchema, SubmenuUpdateSchema


class SubmenuService:
    def __init__(
        self, cache_repository: SubmenuCacheRepository = Depends(), submenu_repository: SubmenuRepository = Depends()
    ):
        self.submenu_repository = submenu_repository
        self.cache_repository = cache_repository

    async def get_all(self, menu_id: UUID) -> list[Submenu]:
        cached_submenus = await self.cache_repository.get_all_submenus(menu_id)
        if cached_submenus:
            return cached_submenus
        db_submenus = await self.submenu_repository.get_all(menu_id=menu_id)
        await self.cache_repository.set_all_submenus(menu_id, db_submenus)
        return db_submenus

    async def get(self, menu_id: UUID, submenu_id: UUID) -> Submenu:
        cached_submenu = await self.cache_repository.get_submenu(menu_id, submenu_id)
        if cached_submenu:
            return cached_submenu
        db_submenu = await self.submenu_repository.get(menu_id=menu_id, submenu_id=submenu_id)
        await self.cache_repository.set_submenu(db_submenu.id, db_submenu)
        return db_submenu

    async def create(self, menu_id: UUID, submenu_data: SubmenuCreateSchema) -> Submenu:
        db_submenu = await self.submenu_repository.create(menu_id=menu_id, submenu_data=submenu_data)
        await self.cache_repository.create_submenu(db_submenu=db_submenu)
        return db_submenu

    async def update(self, menu_id: UUID, submenu_id: UUID, submenu_data: SubmenuUpdateSchema) -> Submenu:
        db_submenu = await self.submenu_repository.update(
            menu_id=menu_id, submenu_id=submenu_id, submenu_data=submenu_data
        )
        await self.cache_repository.update_submenu(db_submenu)
        return db_submenu

    async def delete(self, menu_id: UUID, submenu_id: UUID) -> dict:
        deleted = await self.submenu_repository.delete(menu_id=menu_id, submenu_id=submenu_id)
        await self.cache_repository.delete_submenu(menu_id, submenu_id)
        return deleted

    async def get_all_ids(self, menu_id: UUID) -> list[UUID]:
        return await self.submenu_repository.get_all_ids(menu_id)
