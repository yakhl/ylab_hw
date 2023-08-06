import json
from uuid import UUID

from fastapi import Depends

from ..configs.cache_tags import all_dishes_tag
from ..configs.error_messages import dish_200_deleted_msg
from ..repositories.cache_repository import CacheRepository
from ..repositories.dish_repository import DishRepository
from ..schemas.dish_schemas import DishInSchema


class DishService:
    def __init__(self, cache_repository: CacheRepository = Depends(), dish_repository: DishRepository = Depends()):
        self.dish_repository = dish_repository
        self.cache_repository = cache_repository

    def _get_all_dishes_id(self, menu_id: UUID | str, submenu_id: UUID | str, all_dishes_tag: str) -> str:
        return f'{menu_id}:{submenu_id}:{all_dishes_tag}'

    def get_all(self, menu_id: UUID, submenu_id: UUID) -> list[dict]:
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        cached_dishes = self.cache_repository.get(all_dishes_id)
        if cached_dishes is not None:
            return json.loads(cached_dishes)
        db_dishes = self.dish_repository.get_all(menu_id=menu_id, submenu_id=submenu_id)
        self.cache_repository.set(all_dishes_id, db_dishes)
        return db_dishes

    def get(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> dict:
        cached_dish = self.cache_repository.get(dish_id)
        if cached_dish is not None:
            return json.loads(cached_dish)
        db_dish = self.dish_repository.get(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        self.cache_repository.set(db_dish['id'], db_dish)
        return db_dish

    def create(self, menu_id: UUID, submenu_id: UUID, dish_data: DishInSchema) -> dict:
        db_dish = self.dish_repository.create(menu_id=menu_id, submenu_id=submenu_id, dish_data=dish_data)
        self.cache_repository.flush()
        self.cache_repository.set(db_dish['id'], db_dish)
        return db_dish

    def update(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data: DishInSchema) -> dict:
        all_dishes_id = self._get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        db_dish = self.dish_repository.update(
            menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id, dish_data=dish_data
        )
        self.cache_repository.delete(all_dishes_id)
        self.cache_repository.set(db_dish['id'], db_dish)
        return db_dish

    def delete(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> dict:
        self.dish_repository.delete(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        self.cache_repository.flush()
        return {'status': True, 'message': dish_200_deleted_msg}
