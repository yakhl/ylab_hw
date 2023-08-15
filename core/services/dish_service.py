from uuid import UUID

from fastapi import Depends

from core.models.models import Dish
from core.repositories.cache_repository import CacheRepository
from core.repositories.dish_repository import DishRepository
from core.schemas.dish_schemas import DishCreateSchema, DishUpdateSchema


class DishService:
    def __init__(self, cache_repository: CacheRepository = Depends(), dish_repository: DishRepository = Depends()):
        self.dish_repository = dish_repository
        self.cache_repository = cache_repository

    async def get_all(self, menu_id: UUID, submenu_id: UUID) -> list[Dish]:
        cached_dishes = await self.cache_repository.get_all_dishes(menu_id, submenu_id)
        if cached_dishes:
            return cached_dishes
        db_dishes = await self.dish_repository.get_all(menu_id=menu_id, submenu_id=submenu_id)
        await self.cache_repository.set_all_dishes(menu_id, submenu_id, db_dishes)
        return db_dishes

    async def get(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> Dish:
        cached_dish = await self.cache_repository.get_dish(menu_id, submenu_id, dish_id)
        if cached_dish:
            return cached_dish
        db_dish = await self.dish_repository.get(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        await self.cache_repository.set_dish(db_dish.id, db_dish)
        return db_dish

    async def create(self, menu_id: UUID, submenu_id: UUID, dish_data: DishCreateSchema) -> Dish:
        db_dish = await self.dish_repository.create(menu_id=menu_id, submenu_id=submenu_id, dish_data=dish_data)
        await self.cache_repository.create_dish(menu_id, db_dish)
        return db_dish

    async def update(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data: DishUpdateSchema) -> Dish:
        db_dish = await self.dish_repository.update(
            menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id, dish_data=dish_data
        )
        await self.cache_repository.update_dish(menu_id, db_dish)
        return db_dish

    async def delete(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> dict:
        deleted = await self.dish_repository.delete(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        await self.cache_repository.delete_dish(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        return deleted

    async def get_all_ids(self, submenu_id: UUID) -> list[UUID]:
        return await self.dish_repository.get_all_ids(submenu_id)
