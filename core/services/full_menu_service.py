from fastapi import Depends

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
        return await self.full_menu_repository.get()
