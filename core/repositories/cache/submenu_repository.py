import json
from uuid import UUID

from fastapi import BackgroundTasks, Depends
from redis import asyncio as aioredis

from core.database.redis_db import get_redis
from core.models.models import Submenu
from core.repositories.cache.cache_repository import (
    CacheRepository,
    handle_redis_exceptions,
)


class SubmenuCacheRepository(CacheRepository):
    def __init__(self, background_tasks: BackgroundTasks, redis: aioredis.Redis = Depends(get_redis)):
        self.redis = redis
        self.background_tasks = background_tasks
        super().__init__()

    @handle_redis_exceptions
    async def get_submenu(self, menu_id: UUID | str, submenu_id: UUID | str) -> dict | None:
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        menu_id = f'{self.menu_tag}_{menu_id}'
        if submenu_id not in await self.redis.smembers(f'{self.dependency_tag}:{menu_id}'):
            return None
        submenu_cache = await self.redis.get(submenu_id)
        if submenu_cache is None:
            return None
        return json.loads(submenu_cache)

    @handle_redis_exceptions
    async def set_submenu(self, submenu_id: UUID | str, submenu_data: Submenu) -> None:
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        await self.redis.set(submenu_id, self._serialize_data(submenu_data), self.ttl_sec)

    @handle_redis_exceptions
    async def get_all_submenus(self, menu_id: UUID | str) -> list[dict] | None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        all_submenus_cache = await self.redis.get(all_submenus_id)
        if all_submenus_cache is None:
            return None
        return json.loads(all_submenus_cache)

    @handle_redis_exceptions
    async def set_all_submenus(self, menu_id: UUID | str, submenus_data: list[Submenu]) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        await self.redis.set(all_submenus_id, self._serialize_data(submenus_data), self.ttl_sec)

    @handle_redis_exceptions
    async def create_submenu(self, db_submenu: Submenu) -> None:
        menu_id = f'{self.menu_tag}_{db_submenu.menu_id}'
        submenu_id = f'{self.submenu_tag}_{db_submenu.id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        to_delete = [all_submenus_id, menu_id, self.all_menus_tag, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, self.redis, *to_delete)
        await self.redis.sadd(f'{self.dependency_tag}:{menu_id}', submenu_id)
        await self.redis.set(submenu_id, self._serialize_data(db_submenu), self.ttl_sec)

    @handle_redis_exceptions
    async def update_submenu(self, db_submenu: Submenu) -> None:
        menu_id = f'{self.menu_tag}_{db_submenu.menu_id}'
        submenu_id = f'{self.submenu_tag}_{db_submenu.id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        to_delete = [all_submenus_id, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, self.redis, *to_delete)
        await self.redis.set(submenu_id, self._serialize_data(db_submenu), self.ttl_sec)

    @handle_redis_exceptions
    async def delete_submenu(self, menu_id: UUID | str, submenu_id: UUID | str) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
        to_delete = [
            menu_id,
            self.all_menus_tag,
            submenu_id,
            all_submenus_id,
            f'{self.dependency_tag}:{submenu_id}',
            all_dishes_id,
            self.full_menu_tag,
        ]
        for dish_id in await self.redis.smembers(f'{self.dependency_tag}:{submenu_id}'):
            to_delete.append(dish_id)
        self.background_tasks.add_task(self._srem_cache_keys, self.redis,
                                       f'{self.dependency_tag}:{menu_id}', submenu_id)
        self.background_tasks.add_task(self._delete_cache_keys, self.redis, *to_delete)
