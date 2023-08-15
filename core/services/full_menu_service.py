from fastapi import Depends

from core.repositories.cache.full_menu_repository import FullMenuCacheRepository
from core.repositories.crud.full_menu_repository import FullMenuRepository
from core.schemas.full_menu_schema import Menu


class FullMenuService:
    def __init__(
        self, cache_repository: FullMenuCacheRepository = Depends(), full_menu_repository: FullMenuRepository = Depends()
    ):
        self.full_menu_repository = full_menu_repository
        self.cache_repository = cache_repository

    async def get(self) -> list[Menu]:
        cached_full_menu = await self.cache_repository.get_full_menu()
        if cached_full_menu:
            cached_full_menu
        db_full_menu = await self.full_menu_repository.get()
        await self.cache_repository.set_full_menu(db_full_menu)
        return db_full_menu
