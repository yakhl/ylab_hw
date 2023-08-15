import json
from uuid import UUID

import redis
from fastapi.encoders import jsonable_encoder

from core.models.models import Base


class CacheRepository:
    _was_redis_disconnect = True

    def __init__(self):
        self.all_menus_tag = 'menus'
        self.all_submenus_tag = 'submenus'
        self.all_dishes_tag = 'dishes'
        self.full_menu_tag = 'full_menu'

        self.menu_tag = 'menu'
        self.submenu_tag = 'submenu'
        self.dish_tag = 'dish'
        self.dependency_tag = 'deps'

        self.ttl_sec = 3600

    @staticmethod
    async def _delete_cache_keys(redis_instance, *args: str) -> None:
        await redis_instance.delete(*args)

    @staticmethod
    async def _srem_cache_keys(redis_instance, name: str, value: str) -> None:
        await redis_instance.srem(name, value)

    def _serialize_data(self, item_data: Base | list[Base]) -> str:
        json_compatible_item_data = jsonable_encoder(item_data)
        serialized_item_data = json.dumps(json_compatible_item_data)
        return serialized_item_data

    def _get_all_submenus_id(self, menu_id: UUID | str) -> str:
        return f'{menu_id}:{self.all_submenus_tag}'

    def _get_all_dishes_id(self, menu_id: UUID | str, submenu_id: UUID | str) -> str:
        return f'{menu_id}:{submenu_id}:{self.all_dishes_tag}'


def handle_redis_exceptions(func):
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
