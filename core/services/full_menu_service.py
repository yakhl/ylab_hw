import json

from fastapi import Depends

from ..configs.cache_tags import full_menu_tag
from ..repositories.cache_repository import CacheRepository
from ..repositories.full_menu_repository import FullMenuRepository
from ..schemas.full_menu_schema import Menu
from .main_service import MainService


class FullMenuService(MainService):
    def __init__(
        self, cache_repository: CacheRepository = Depends(), full_menu_repository: FullMenuRepository = Depends()
    ):
        self.full_menu_repository = full_menu_repository
        self.cache_repository = cache_repository

    async def get(self) -> list[Menu]:
        cached_full_menu = await self.cache_repository.get(full_menu_tag)
        if cached_full_menu is not None:
            return json.loads(cached_full_menu)
        db_full_menu = await self.full_menu_repository.get()
        await self.cache_repository.set(full_menu_tag, db_full_menu)
        return db_full_menu
