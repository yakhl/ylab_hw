import json
from uuid import UUID

from fastapi import BackgroundTasks, Depends
from redis import asyncio as aioredis

from core.database.redis_db import get_redis
from core.models.models import Dish
from core.repositories.cache.cache_repository import (
    CacheRepository,
    handle_redis_exceptions,
)


class DishCacheRepository(CacheRepository):
    def __init__(self, background_tasks: BackgroundTasks, redis: aioredis.Redis = Depends(get_redis)):
        self.redis = redis
        self.background_tasks = background_tasks
        super().__init__()

    @handle_redis_exceptions
    async def get_dish(self, menu_id: UUID | str, submenu_id: UUID | str, dish_id: UUID | str) -> dict | None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        dish_id = f'{self.dish_tag}_{dish_id}'
        if submenu_id not in await self.redis.smembers(f'{self.dependency_tag}:{menu_id}'):
            return None
        if dish_id not in await self.redis.smembers(f'{self.dependency_tag}:{submenu_id}'):
            return None
        dish_cache = await self.redis.get(dish_id)
        if dish_cache is None:
            return None
        return json.loads(dish_cache)

    @handle_redis_exceptions
    async def set_dish(self, dish_id: UUID | str, dish_data: Dish) -> None:
        dish_id = f'{self.dish_tag}_{dish_id}'
        await self.redis.set(dish_id, self._serialize_data(dish_data), self.ttl_sec)

    @handle_redis_exceptions
    async def get_all_dishes(self, menu_id: UUID | str, submenu_id: UUID | str) -> list[dict] | None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        if submenu_id not in await self.redis.smembers(f'{self.dependency_tag}:{menu_id}'):
            return None
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
        all_dishes_cache = await self.redis.get(all_dishes_id)
        if all_dishes_cache is None:
            return None
        return json.loads(all_dishes_cache)

    @handle_redis_exceptions
    async def set_all_dishes(self, menu_id: UUID | str, submenu_id: UUID | str, dish_data: Dish) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
        await self.redis.set(all_dishes_id, self._serialize_data(dish_data), self.ttl_sec)

    @handle_redis_exceptions
    async def create_dish(self, menu_id: UUID | str, db_dish: Dish) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{db_dish.submenu_id}'
        dish_id = f'{self.dish_tag}_{db_dish.id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
        to_delete = [all_dishes_id, submenu_id, all_submenus_id, menu_id, self.all_menus_tag, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, self.redis, *to_delete)
        await self.redis.sadd(f'{self.dependency_tag}:{submenu_id}', dish_id)
        await self.redis.set(dish_id, self._serialize_data(db_dish), self.ttl_sec)

    @handle_redis_exceptions
    async def update_dish(self, menu_id: UUID | str, db_dish: Dish) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{db_dish.submenu_id}'
        dish_id = f'{self.dish_tag}_{db_dish.id}'
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
        to_delete = [all_dishes_id, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, self.redis, *to_delete)
        await self.redis.set(dish_id, self._serialize_data(db_dish), self.ttl_sec)

    @handle_redis_exceptions
    async def delete_dish(self, menu_id: UUID | str, submenu_id: UUID | str, dish_id: UUID | str) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        dish_id = f'{self.dish_tag}_{dish_id}'
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
        all_submenus_id = self._get_all_submenus_id(menu_id)
        self.background_tasks.add_task(self._srem_cache_keys, self.redis,
                                       f'{self.dependency_tag}:{submenu_id}', dish_id)
        to_delete = [
            dish_id,
            all_dishes_id,
            submenu_id,
            all_submenus_id,
            menu_id,
            self.all_menus_tag,
            self.full_menu_tag,
        ]
        self.background_tasks.add_task(self._delete_cache_keys, self.redis, *to_delete)
