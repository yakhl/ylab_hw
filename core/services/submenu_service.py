import json
from uuid import UUID

from fastapi import Depends

from ..configs.cache_tags import all_submenus_tag
from ..configs.error_messages import submenu_200_deleted_msg
from ..models.models import Submenu
from ..repositories.cache_repository import CacheRepository
from ..repositories.submenu_repository import SubmenuRepository
from ..schemas.submenu_schemas import SubmenuInSchema
from .main_service import MainService


class SubmenuService(MainService):
    def __init__(
        self, cache_repository: CacheRepository = Depends(), submenu_repository: SubmenuRepository = Depends()
    ):
        self.submenu_repository = submenu_repository
        self.cache_repository = cache_repository

    async def get_all(self, menu_id: UUID) -> list[Submenu]:
        all_submenus_id = self.get_all_submenus_id(menu_id, all_submenus_tag)
        cached_submenus = await self.cache_repository.get(all_submenus_id)
        if cached_submenus is not None:
            return json.loads(cached_submenus)
        db_submenus = await self.submenu_repository.get_all(menu_id=menu_id)
        await self.cache_repository.set(all_submenus_id, db_submenus)
        return db_submenus

    async def get(self, menu_id: UUID, submenu_id: UUID) -> Submenu:
        cached_submenu = await self.cache_repository.get(submenu_id)
        if cached_submenu is not None:
            return json.loads(cached_submenu)
        db_submenu = await self.submenu_repository.get(menu_id=menu_id, submenu_id=submenu_id)
        await self.cache_repository.set(db_submenu.id, db_submenu)
        return db_submenu

    async def create(self, menu_id: UUID, submenu_data: SubmenuInSchema) -> Submenu:
        db_submenu = await self.submenu_repository.create(menu_id=menu_id, submenu_data=submenu_data)
        await self.cache_repository.create_submenu(db_submenu=db_submenu)
        return db_submenu

    async def update(self, menu_id: UUID, submenu_id: UUID, submenu_data: SubmenuInSchema) -> Submenu:
        db_submenu = await self.submenu_repository.update(
            menu_id=menu_id, submenu_id=submenu_id, submenu_data=submenu_data
        )
        await self.cache_repository.update_submenu(db_submenu)
        return db_submenu

    async def delete(self, menu_id: UUID, submenu_id: UUID) -> dict:
        await self.submenu_repository.delete(menu_id=menu_id, submenu_id=submenu_id)
        await self.cache_repository.delete_submenu(menu_id, submenu_id)
        return {'status': True, 'message': submenu_200_deleted_msg}

    async def get_all_ids(self, menu_id: UUID) -> list[UUID]:
        return await self.submenu_repository.get_all_ids(menu_id)
