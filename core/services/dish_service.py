import json
from uuid import UUID

from fastapi import Depends

from ..configs.cache_tags import all_dishes_tag
from ..configs.error_messages import dish_200_deleted_msg
from ..models.models import Dish
from ..repositories.cache_repository import CacheRepository
from ..repositories.dish_repository import DishRepository
from ..schemas.dish_schemas import DishInSchema
from .main_service import MainService


class DishService(MainService):
    def __init__(self, cache_repository: CacheRepository = Depends(), dish_repository: DishRepository = Depends()):
        self.dish_repository = dish_repository
        self.cache_repository = cache_repository

    async def get_all(self, menu_id: UUID, submenu_id: UUID) -> list[Dish]:
        all_dishes_id = self.get_all_dishes_id(menu_id, submenu_id, all_dishes_tag)
        cached_dishes = await self.cache_repository.get(all_dishes_id)
        if cached_dishes is not None:
            return json.loads(cached_dishes)
        db_dishes = await self.dish_repository.get_all(menu_id=menu_id, submenu_id=submenu_id)
        await self.cache_repository.set(all_dishes_id, db_dishes)
        return db_dishes

    async def get(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> Dish:
        cached_dish = await self.cache_repository.get(dish_id)
        if cached_dish is not None:
            return json.loads(cached_dish)
        db_dish = await self.dish_repository.get(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        await self.cache_repository.set(db_dish.id, db_dish)
        return db_dish

    async def create(self, menu_id: UUID, submenu_id: UUID, dish_data: DishInSchema) -> Dish:
        db_dish = await self.dish_repository.create(menu_id=menu_id, submenu_id=submenu_id, dish_data=dish_data)
        await self.cache_repository.create_dish(menu_id, db_dish)
        return db_dish

    async def update(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data: DishInSchema) -> Dish:
        db_dish = await self.dish_repository.update(
            menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id, dish_data=dish_data
        )
        await self.cache_repository.update_dish(menu_id, db_dish)
        return db_dish

    async def delete(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> dict:
        await self.dish_repository.delete(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        await self.cache_repository.delete_dish(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        return {'status': True, 'message': dish_200_deleted_msg}

    async def get_all_ids(self, submenu_id: UUID) -> list[UUID]:
        return await self.dish_repository.get_all_ids(submenu_id)
