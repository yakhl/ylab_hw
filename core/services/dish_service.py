from uuid import UUID

from fastapi import Depends

from ..models.models import Dish
from ..repositories.dish_repository import DishRepository
from ..schemas.dish_schemas import DishInSchema


class DishService:
    def __init__(self, repository: DishRepository = Depends()):
        self.repository = repository

    def get_all(self, menu_id: UUID, submenu_id: UUID) -> list[Dish]:
        return self.repository.get_all(menu_id=menu_id, submenu_id=submenu_id)

    def get(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> Dish:
        return self.repository.get(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)

    def create(self, menu_id: UUID, submenu_id: UUID, dish_data: DishInSchema) -> Dish:
        return self.repository.create(menu_id=menu_id, submenu_id=submenu_id, dish_data=dish_data)

    def update(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data: DishInSchema) -> Dish:
        return self.repository.update(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id, dish_data=dish_data)

    def delete(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> dict:
        return self.repository.delete(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
