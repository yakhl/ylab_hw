import json
from uuid import UUID

import redis
from fastapi import BackgroundTasks, Depends
from fastapi.encoders import jsonable_encoder
from redis import asyncio as aioredis

from core.database.redis_db import get_redis
from core.models.models import Base, Dish, Menu, Submenu
from core.schemas.full_menu_schema import Menu as MenuSchema


class CacheRepository:
    _was_redis_disconnect = True

    def __init__(self, background_tasks: BackgroundTasks, redis: aioredis.Redis = Depends(get_redis)):
        self.redis = redis
        self.ttl_sec = 3600
        self.background_tasks = background_tasks

        self.all_menus_tag = 'menus'
        self.all_submenus_tag = 'submenus'
        self.all_dishes_tag = 'dishes'
        self.full_menu_tag = 'full_menu'

        self.menu_tag = 'menu'
        self.submenu_tag = 'submenu'
        self.dish_tag = 'dish'
        self.dependency_tag = 'deps'

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

    async def _delete_cache_keys(self, *args: str) -> None:
        await self.redis.delete(*args)

    async def _srem_cache_keys(self, name: str, value: str) -> None:
        await self.redis.srem(name, value)

    def _serialize_data(self, item_data: Base | list[Base]) -> str:
        json_compatible_item_data = jsonable_encoder(item_data)
        serialized_item_data = json.dumps(json_compatible_item_data)
        return serialized_item_data

    def _get_all_submenus_id(self, menu_id: UUID | str) -> str:
        return f'{menu_id}:{self.all_submenus_tag}'

    def _get_all_dishes_id(self, menu_id: UUID | str, submenu_id: UUID | str) -> str:
        return f'{menu_id}:{submenu_id}:{self.all_dishes_tag}'

    @_handle_redis_exceptions
    async def get_menu(self, menu_id: UUID | str) -> dict | None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        menu_cache = await self.redis.get(menu_id)
        if menu_cache is None:
            return None
        return json.loads(menu_cache)

    @_handle_redis_exceptions
    async def set_menu(self, menu_id: UUID | str, menu_data: Menu) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        await self.redis.set(menu_id, self._serialize_data(menu_data), self.ttl_sec)

    @_handle_redis_exceptions
    async def get_all_menus(self) -> list[dict] | None:
        all_menus_cache = await self.redis.get(self.all_menus_tag)
        if all_menus_cache is None:
            return None
        return json.loads(all_menus_cache)

    @_handle_redis_exceptions
    async def set_all_menus(self, menus_data: list[Menu]) -> None:
        await self.redis.set(self.all_menus_tag, self._serialize_data(menus_data), self.ttl_sec)

    @_handle_redis_exceptions
    async def create_menu(self, db_menu: Menu) -> None:
        menu_id = f'{self.menu_tag}_{db_menu.id}'
        to_delete = [self.all_menus_tag, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.set(menu_id, self._serialize_data(db_menu), self.ttl_sec)

    @_handle_redis_exceptions
    async def update_menu(self, db_menu: Menu) -> None:
        menu_id = f'{self.menu_tag}_{db_menu.id}'
        to_delete = [self.all_menus_tag, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.set(menu_id, self._serialize_data(db_menu), self.ttl_sec)

    @_handle_redis_exceptions
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
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)

    @_handle_redis_exceptions
    async def get_submenu(self, menu_id: UUID | str, submenu_id: UUID | str) -> dict | None:
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        menu_id = f'{self.menu_tag}_{menu_id}'
        if submenu_id not in await self.redis.smembers(f'{self.dependency_tag}:{menu_id}'):
            return None
        submenu_cache = await self.redis.get(submenu_id)
        if submenu_cache is None:
            return None
        return json.loads(submenu_cache)

    @_handle_redis_exceptions
    async def set_submenu(self, submenu_id: UUID | str, submenu_data: Submenu) -> None:
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        await self.redis.set(submenu_id, self._serialize_data(submenu_data), self.ttl_sec)

    @_handle_redis_exceptions
    async def get_all_submenus(self, menu_id: UUID | str) -> list[dict] | None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        all_submenus_cache = await self.redis.get(all_submenus_id)
        if all_submenus_cache is None:
            return None
        return json.loads(all_submenus_cache)

    @_handle_redis_exceptions
    async def set_all_submenus(self, menu_id: UUID | str, submenus_data: list[Submenu]) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        await self.redis.set(all_submenus_id, self._serialize_data(submenus_data), self.ttl_sec)

    @_handle_redis_exceptions
    async def create_submenu(self, db_submenu: Submenu) -> None:
        menu_id = f'{self.menu_tag}_{db_submenu.menu_id}'
        submenu_id = f'{self.submenu_tag}_{db_submenu.id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        to_delete = [all_submenus_id, menu_id, self.all_menus_tag, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.sadd(f'{self.dependency_tag}:{menu_id}', submenu_id)
        await self.redis.set(submenu_id, self._serialize_data(db_submenu), self.ttl_sec)

    @_handle_redis_exceptions
    async def update_submenu(self, db_submenu: Submenu) -> None:
        menu_id = f'{self.menu_tag}_{db_submenu.menu_id}'
        submenu_id = f'{self.submenu_tag}_{db_submenu.id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        to_delete = [all_submenus_id, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.set(submenu_id, self._serialize_data(db_submenu), self.ttl_sec)

    @_handle_redis_exceptions
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
        self.background_tasks.add_task(self._srem_cache_keys, f'{self.dependency_tag}:{menu_id}', submenu_id)
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)

    @_handle_redis_exceptions
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

    @_handle_redis_exceptions
    async def set_dish(self, dish_id: UUID | str, dish_data: Dish) -> None:
        dish_id = f'{self.dish_tag}_{dish_id}'
        await self.redis.set(dish_id, self._serialize_data(dish_data), self.ttl_sec)

    @_handle_redis_exceptions
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

    @_handle_redis_exceptions
    async def set_all_dishes(self, menu_id: UUID | str, submenu_id: UUID | str, dish_data: Dish) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
        await self.redis.set(all_dishes_id, self._serialize_data(dish_data), self.ttl_sec)

    @_handle_redis_exceptions
    async def create_dish(self, menu_id: UUID | str, db_dish: Dish) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{db_dish.submenu_id}'
        dish_id = f'{self.dish_tag}_{db_dish.id}'
        all_submenus_id = self._get_all_submenus_id(menu_id)
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
        to_delete = [all_dishes_id, submenu_id, all_submenus_id, menu_id, self.all_menus_tag, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.sadd(f'{self.dependency_tag}:{submenu_id}', dish_id)
        await self.redis.set(dish_id, self._serialize_data(db_dish), self.ttl_sec)

    @_handle_redis_exceptions
    async def update_dish(self, menu_id: UUID | str, db_dish: Dish) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{db_dish.submenu_id}'
        dish_id = f'{self.dish_tag}_{db_dish.id}'
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
        to_delete = [all_dishes_id, self.full_menu_tag]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)
        await self.redis.set(dish_id, self._serialize_data(db_dish), self.ttl_sec)

    @_handle_redis_exceptions
    async def delete_dish(self, menu_id: UUID | str, submenu_id: UUID | str, dish_id: UUID | str) -> None:
        menu_id = f'{self.menu_tag}_{menu_id}'
        submenu_id = f'{self.submenu_tag}_{submenu_id}'
        dish_id = f'{self.dish_tag}_{dish_id}'
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id)
        all_submenus_id = self._get_all_submenus_id(menu_id)
        self.background_tasks.add_task(self._srem_cache_keys, f'{self.dependency_tag}:{submenu_id}', dish_id)
        to_delete = [
            dish_id,
            all_dishes_id,
            submenu_id,
            all_submenus_id,
            menu_id,
            self.all_menus_tag,
            self.full_menu_tag,
        ]
        self.background_tasks.add_task(self._delete_cache_keys, *to_delete)

    @_handle_redis_exceptions
    async def get_full_menu(self) -> list[dict] | None:
        full_menu_cache = await self.redis.get(self.full_menu_tag)
        if full_menu_cache is None:
            return None
        return json.loads(full_menu_cache)

    @_handle_redis_exceptions
    async def set_full_menu(self, full_menu_data: list[MenuSchema]) -> None:
        await self.redis.set(self.full_menu_tag, self._serialize_data(full_menu_data), self.ttl_sec)
