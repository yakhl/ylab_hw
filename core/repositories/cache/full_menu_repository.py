import json

from fastapi import BackgroundTasks, Depends
from redis import asyncio as aioredis

from core.database.redis_db import get_redis
from core.repositories.cache.cache_repository import (
    CacheRepository,
    handle_redis_exceptions,
)
from core.schemas.full_menu_schema import Menu as MenuSchema


class FullMenuCacheRepository(CacheRepository):
    def __init__(self, background_tasks: BackgroundTasks, redis: aioredis.Redis = Depends(get_redis)):
        self.redis = redis
        self.background_tasks = background_tasks
        super().__init__()

    @handle_redis_exceptions
    async def get_full_menu(self) -> list[dict] | None:
        full_menu_cache = await self.redis.get(self.full_menu_tag)
        if full_menu_cache is None:
            return None
        return json.loads(full_menu_cache)

    @handle_redis_exceptions
    async def set_full_menu(self, full_menu_data: list[MenuSchema]) -> None:
        await self.redis.set(self.full_menu_tag, self._serialize_data(full_menu_data), self.ttl_sec)
