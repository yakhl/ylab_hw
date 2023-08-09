import json
from uuid import UUID

import redis
from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from ..configs.cache_tags import all_dishes_tag, all_menus_tag, all_submenus_tag
from ..database.redis_db import get_redis
from ..services.main_service import MainService


class CacheRepository:
    _was_redis_disconnect = True

    def __init__(self, redis: redis.Redis = Depends(get_redis)):
        self.redis = redis
        self.ttl_sec = 3600

    @staticmethod
    def _handle_redis_exceptions(func):
        def wrapper(self, *args, **kwargs):
            try:
                if CacheRepository._was_redis_disconnect:
                    self.redis.flushdb()
                result = func(self, *args, **kwargs)
                CacheRepository._was_redis_disconnect = False
                return result
            except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError):
                CacheRepository._was_redis_disconnect = True
                return None

        return wrapper

    def _serialize_data(self, item_data: dict | list[dict]) -> str:
        json_compatible_item_data = jsonable_encoder(item_data)
        serialized_item_data = json.dumps(json_compatible_item_data)
        return serialized_item_data

    @_handle_redis_exceptions
    def set(self, item_id: UUID | str, item_data: dict | list[dict]) -> None:
        self.redis.set(str(item_id), self._serialize_data(item_data), self.ttl_sec)

    @_handle_redis_exceptions
    def get(self, item_id: UUID | str) -> str | None:
        menu_cache = self.redis.get(str(item_id))
        if menu_cache is None:
            return None
        return menu_cache

    @_handle_redis_exceptions
    def create_menu(self, db_menu: dict) -> None:
        menu_id = str(db_menu['id'])
        self.redis.delete(all_menus_tag)
        self.redis.set(menu_id, self._serialize_data(db_menu), self.ttl_sec)

    @_handle_redis_exceptions
    def update_menu(self, db_menu: dict) -> None:
        menu_id = str(db_menu['id'])
        self.redis.delete(all_menus_tag)
        self.redis.set(menu_id, self._serialize_data(db_menu), self.ttl_sec)

    @_handle_redis_exceptions
    def delete_menu(self, menu_id: UUID | str) -> None:
        menu_id = str(menu_id)
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        to_delete = [all_menus_tag, menu_id, all_submenus_id, f'deps:{menu_id}']
        for submenu_id in self.redis.smembers(f'deps:{menu_id}'):
            for dish_id in self.redis.smembers(f'deps:{submenu_id}'):
                to_delete.append(dish_id)
            all_dishes_id = MainService.get_all_dishes_id(menu_id, submenu_id, all_submenus_tag)
            to_delete.extend([all_dishes_id, submenu_id, f'deps:{submenu_id}'])
        self.redis.delete(*to_delete)

    @_handle_redis_exceptions
    def create_submenu(self, db_submenu: dict) -> None:
        menu_id, submenu_id = str(db_submenu['menu_id']), str(db_submenu['id'])
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        self.redis.delete(all_submenus_id, menu_id, all_menus_tag)
        self.redis.sadd(f'deps:{menu_id}', submenu_id)
        self.redis.set(submenu_id, self._serialize_data(db_submenu), self.ttl_sec)

    @_handle_redis_exceptions
    def update_submenu(self, db_submenu: dict) -> None:
        menu_id, submenu_id = str(db_submenu['menu_id']), str(db_submenu['id'])
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        self.redis.delete(all_submenus_id)
        self.redis.set(submenu_id, self._serialize_data(db_submenu), self.ttl_sec)

    @_handle_redis_exceptions
    def delete_submenu(self, menu_id: UUID | str, submenu_id: UUID | str) -> None:
        menu_id, submenu_id = str(menu_id), str(submenu_id)
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        all_dishes_id = MainService.get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        to_delete = [menu_id, all_menus_tag, submenu_id, all_submenus_id, f'deps:{submenu_id}', all_dishes_id]
        for dish_id in self.redis.smembers(f'deps:{submenu_id}'):
            to_delete.append(dish_id)
        self.redis.srem(f'deps:{menu_id}', submenu_id)
        self.redis.delete(*to_delete)

    @_handle_redis_exceptions
    def create_dish(self, menu_id: UUID | str, db_dish: dict) -> None:
        menu_id, submenu_id, dish_id = str(menu_id), str(db_dish['submenu_id']), str(db_dish['id'])
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        all_dishes_id = MainService.get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        self.redis.delete(all_dishes_id, submenu_id, all_submenus_id, menu_id, all_menus_tag)
        self.redis.sadd(f'deps:{submenu_id}', dish_id)
        self.redis.set(dish_id, self._serialize_data(db_dish), self.ttl_sec)

    @_handle_redis_exceptions
    def update_dish(self, menu_id: UUID | str, db_dish: dict) -> None:
        submenu_id, dish_id = str(db_dish['submenu_id']), str(db_dish['id'])
        all_dishes_id = MainService.get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        self.redis.delete(all_dishes_id)
        self.redis.set(dish_id, self._serialize_data(db_dish), self.ttl_sec)

    @_handle_redis_exceptions
    def delete_dish(self, menu_id: UUID | str, submenu_id: UUID | str, dish_id: UUID | str) -> None:
        menu_id, submenu_id, dish_id = str(menu_id), str(submenu_id), str(dish_id)
        all_dishes_id = MainService.get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        all_submenus_id = MainService.get_all_submenus_id(menu_id, all_submenus_tag)
        self.redis.srem(f'deps:{submenu_id}', dish_id)
        self.redis.delete(dish_id, all_dishes_id, submenu_id, all_submenus_id, menu_id, all_menus_tag)
