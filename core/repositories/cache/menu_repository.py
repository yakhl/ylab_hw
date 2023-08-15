import json
from uuid import UUID

from fastapi import BackgroundTasks, Depends
from redis import asyncio as aioredis

from core.database.redis_db import get_redis
from core.models.models import Menu
from core.repositories.cache.cache_repository import (
    CacheRepository,
    handle_redis_exceptions,
)


class MenuCacheRepository(CacheRepository):
    def __init__(self, background_tasks: BackgroundTasks, redis: aioredis.Redis = Depends(get_redis)):
        self.redis = redis
        self.background_tasks = background_tasks
        super().__init__()

    @handle_redis_exceptions
    async def get_menu(self, menu_id: UUID | str) -> dict | None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        menu_cache = await self.redis.get(menu_id)
        if menu_cache is None:
            return None
        return json.loads(menu_cache)

    @handle_redis_exceptions
    async def set_menu(self, menu_id: UUID | str, menu_data: Menu) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        await self.redis.set(menu_id, self._serialize_data(menu_data), self.ttl_sec)

    @handle_redis_exceptions
    async def get_all_menus(self) -> list[dict] | None:
        all_menus_cache = await self.redis.get(self.all_menus_tag)
        if all_menus_cache is None:
            return None
        return json.loads(all_menus_cache)

    @handle_redis_exceptions
    async def set_all_menus(self, menus_data: list[Menu]) -> None:
        await self.redis.set(self.all_menus_tag, self._serialize_data(menus_data), self.ttl_sec)

    @handle_redis_exceptions
    async def create_menu(self, db_menu: Menu) -> None:
        menu_id = f'{self.menu_tag}_{db_menu.id}'
        to_delete = [self.all_menus_tag, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, self.redis, *to_delete)
        await self.redis.set(menu_id, self._serialize_data(db_menu), self.ttl_sec)

    @handle_redis_exceptions
    async def update_menu(self, db_menu: Menu) -> None:
        menu_id = f'{self.menu_tag}_{db_menu.id}'
        to_delete = [self.all_menus_tag, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, self.redis, *to_delete)
        await self.redis.set(menu_id, self._serialize_data(db_menu), self.ttl_sec)

    @handle_redis_exceptions
    async def delete_menu(self, menu_id: UUID | str) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        to_delete = [
            self.all_menus_tag,
            menu_id,
            all_submenus_id,
            f'{self.dependency_tag}:{menu_id}',
            self.full_menu_tag,
        ]
        for submenu_id in await self.redis.smembers(f'{self.dependency_tag}:{menu_id}'):
            for dish_id in await self.redis.smembers(f'{self.dependency_tag}:{submenu_id}'):
                to_delete.append(dish_id)
            all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
            to_delete.extend([all_dishes_id, submenu_id, f'{self.dependency_tag}:{submenu_id}'])
        self.background_tasks.add_task(self._delete_cache_keys, self.redis, *to_delete)
