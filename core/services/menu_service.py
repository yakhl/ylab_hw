from uuid import UUID

from fastapi import Depends

from ..models.models import Menu
from ..repositories.menu_repository import MenuRepository
from ..schemas.menu_schemas import MenuInSchema


class MenuService:
    def __init__(self, repository: MenuRepository = Depends()):
        self.repository = repository

    def get_all(self) -> list[Menu]:
        return self.repository.get_all()

    def get(self, id: UUID) -> Menu:
        return self.repository.get(id=id)

    def create(self, menu_data: MenuInSchema) -> Menu:
        return self.repository.create(menu_data=menu_data)

    def update(self, id: UUID, menu_data: MenuInSchema) -> Menu:
        return self.repository.update(id=id, menu_data=menu_data)

    def delete(self, id: UUID) -> dict:
        return self.repository.delete(id=id)
