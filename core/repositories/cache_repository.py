import json
from uuid import UUID

import redis
from fastapi import BackgroundTasks, Depends
from fastapi.encoders import jsonable_encoder
from redis import asyncio as aioredis

from ..configs.cache_tags import (
    all_dishes_tag,
    all_menus_tag,
    all_submenus_tag,
    full_menu_tag,
)
from ..database.redis_db import get_redis
from ..models.models import Dish, Menu, Submenu
from ..services.main_service import MainService


class CacheRepository:
    _was_redis_disconnect = True

    def __init__(self, background_tasks: BackgroundTasks, redis: aioredis.Redis = Depends(get_redis)):
        self.redis = redis
        self.ttl_sec = 3600
        self.background_tasks = background_tasks

    @staticmethod
    def _handle_redis_exceptions(func):
        async def wrapper(self, *args, **kwargs):
            try:
                if CacheRepository._was_redis_disconnect:
                    await self.redis.flushdb()
                result = await func(self, *args, **kwargs)
                CacheRepository._was_redis_disconnect = False
                return result
            except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError):
                CacheRepository._was_redis_disconnect = True
                return None

        return wrapper

    async def _delete_cache_keys(self, *args) -> None:
        await self.redis.delete(*args)

    async def _srem_cache_keys(self, name, value) -> None:
        await self.redis.srem(name, value)

    def _serialize_data(self, item_data: dict | list[dict]) -> str:
        json_compatible_item_data = jsonable_encoder(item_data)
        serialized_item_data = json.dumps(json_compatible_item_data)
        return serialized_item_data

    @_handle_redis_exceptions
    async def set(self, item_id: UUID | str, item_data: dict | list[dict]) -> None:
        await self.redis.set(str(item_id), self._serialize_data(item_data), self.ttl_sec)

    @_handle_redis_exceptions
    async def get(self, item_id: UUID | str) -> str | None:
        menu_cache = await self.redis.get(str(item_id))
        if menu_cache is None:
            return None
        return menu_cache

    @_handle_redis_exceptions
    async def create_menu(self, db_menu: Menu) -> None:
        menu_id = str(db_menu.id)
        to_delete = [all_menus_tag, full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.set(menu_id, self._serialize_data(db_menu), self.ttl_sec)

    @_handle_redis_exceptions
    async def update_menu(self, db_menu: Menu) -> None:
        menu_id = str(db_menu.id)
        to_delete = [all_menus_tag, full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.set(menu_id, self._serialize_data(db_menu), self.ttl_sec)

    @_handle_redis_exceptions
    async def delete_menu(self, menu_id: UUID | str) -> None:
        menu_id = str(menu_id)
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        to_delete = [all_menus_tag, menu_id, all_submenus_id, f'deps:{menu_id}', full_menu_tag]
        for submenu_id in await self.redis.smembers(f'deps:{menu_id}'):
            for dish_id in await self.redis.smembers(f'deps:{submenu_id}'):
                to_delete.append(dish_id)
            all_dishes_id = MainService.get_all_dishes_id(menu_id, submenu_id, all_submenus_tag)
            to_delete.extend([all_dishes_id, submenu_id, f'deps:{submenu_id}'])
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)

    @_handle_redis_exceptions
    async def create_submenu(self, db_submenu: Submenu) -> None:
        menu_id, submenu_id = str(db_submenu.menu_id), str(db_submenu.id)
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        to_delete = [all_submenus_id, menu_id, all_menus_tag, full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.sadd(f'deps:{menu_id}', submenu_id)
        await self.redis.set(submenu_id, self._serialize_data(db_submenu), self.ttl_sec)

    @_handle_redis_exceptions
    async def update_submenu(self, db_submenu: Submenu) -> None:
        menu_id, submenu_id = str(db_submenu.menu_id), str(db_submenu.id)
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        to_delete = [all_submenus_id, full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.set(submenu_id, self._serialize_data(db_submenu), self.ttl_sec)

    @_handle_redis_exceptions
    async def delete_submenu(self, menu_id: UUID | str, submenu_id: UUID | str) -> None:
        menu_id, submenu_id = str(menu_id), str(submenu_id)
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        all_dishes_id = MainService.get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        to_delete = [
            menu_id,
            all_menus_tag,
            submenu_id,
            all_submenus_id,
            f'deps:{submenu_id}',
            all_dishes_id,
            full_menu_tag,
        ]
        for dish_id in await self.redis.smembers(f'deps:{submenu_id}'):
            to_delete.append(dish_id)
        self.background_tasks.add_task(self._srem_cache_keys, f'deps:{menu_id}', submenu_id)
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)

    @_handle_redis_exceptions
    async def create_dish(self, menu_id: UUID | str, db_dish: Dish) -> None:
        menu_id, submenu_id, dish_id = str(menu_id), str(db_dish.submenu_id), str(db_dish.id)
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        all_dishes_id = MainService.get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        to_delete = [all_dishes_id, submenu_id, all_submenus_id, menu_id, all_menus_tag, full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.sadd(f'deps:{submenu_id}', dish_id)
        await self.redis.set(dish_id, self._serialize_data(db_dish), self.ttl_sec)

    @_handle_redis_exceptions
    async def update_dish(self, menu_id: UUID | str, db_dish: Dish) -> None:
        submenu_id, dish_id = str(db_dish.submenu_id), str(db_dish.id)
        all_dishes_id = MainService.get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        to_delete = [all_dishes_id, full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.set(dish_id, self._serialize_data(db_dish), self.ttl_sec)

    @_handle_redis_exceptions
    async def delete_dish(self, menu_id: UUID | str, submenu_id: UUID | str, dish_id: UUID | str) -> None:
        menu_id, submenu_id, dish_id = str(menu_id), str(submenu_id), str(dish_id)
        all_dishes_id = MainService.get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        self.background_tasks.add_task(self._srem_cache_keys, f'deps:{submenu_id}', dish_id)
        to_delete = [dish_id, all_dishes_id, submenu_id, all_submenus_id, menu_id, all_menus_tag, full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
