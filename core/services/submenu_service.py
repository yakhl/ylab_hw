import json
from uuid import UUID

from fastapi import Depends

from ..configs.cache_tags import all_submenus_tag
from ..configs.error_messages import submenu_200_deleted_msg
from ..repositories.cache_repository import CacheRepository
from ..repositories.submenu_repository import SubmenuRepository
from ..schemas.submenu_schemas import SubmenuInSchema


class SubmenuService:
    def __init__(
        self, cache_repository: CacheRepository = Depends(), submenu_repository: SubmenuRepository = Depends()
    ):
        self.submenu_repository = submenu_repository
        self.cache_repository = cache_repository

    def _get_all_submenus_id(self, menu_id: UUID | str, all_submenus_tag: str) -> str:
        return f'{menu_id}:{all_submenus_tag}'

    def get_all(self, menu_id: UUID) -> list[dict]:
        all_submenus_id = self._get_all_submenus_id(menu_id, all_submenus_tag)
        cached_submenus = self.cache_repository.get(all_submenus_id)
        if cached_submenus is not None:
            return json.loads(cached_submenus)
        db_submenus = self.submenu_repository.get_all(menu_id=menu_id)
        self.cache_repository.set(all_submenus_id, db_submenus)
        return db_submenus

    def get(self, menu_id: UUID, submenu_id: UUID) -> dict:
        cached_submenu = self.cache_repository.get(submenu_id)
        if cached_submenu is not None:
            return json.loads(cached_submenu)
        db_submenu = self.submenu_repository.get(menu_id=menu_id, submenu_id=submenu_id)
        self.cache_repository.set(db_submenu['id'], db_submenu)
        return db_submenu

    def create(self, menu_id: UUID, submenu_data: SubmenuInSchema) -> dict:
        db_submenu = self.submenu_repository.create(menu_id=menu_id, submenu_data=submenu_data)
        self.cache_repository.flush()
        self.cache_repository.set(db_submenu['id'], db_submenu)
        return db_submenu

    def update(self, menu_id: UUID, submenu_id: UUID, submenu_data: SubmenuInSchema) -> dict:
        all_submenus_id = self._get_all_submenus_id(menu_id, all_submenus_tag)
        db_submenu = self.submenu_repository.update(menu_id=menu_id, submenu_id=submenu_id, submenu_data=submenu_data)
        self.cache_repository.delete(all_submenus_id)
        self.cache_repository.set(db_submenu['id'], db_submenu)
        return db_submenu

    def delete(self, menu_id: UUID, submenu_id: UUID) -> dict:
        self.submenu_repository.delete(menu_id=menu_id, submenu_id=submenu_id)
        self.cache_repository.flush()
        return {'status': True, 'message': submenu_200_deleted_msg}
