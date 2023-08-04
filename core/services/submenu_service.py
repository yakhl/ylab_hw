from uuid import UUID

from fastapi import Depends

from ..models.models import Submenu
from ..repositories.submenu_repository import SubmenuRepository
from ..schemas.submenu_schemas import SubmenuInSchema


class SubmenuService:
    def __init__(self, repository: SubmenuRepository = Depends()):
        self.repository = repository

    def get_all(self, menu_id: UUID) -> list[Submenu]:
        return self.repository.get_all(menu_id=menu_id)

    def get(self, menu_id: UUID, submenu_id: UUID) -> Submenu:
        return self.repository.get(menu_id=menu_id, submenu_id=submenu_id)

    def create(self, menu_id: UUID, submenu_data: SubmenuInSchema) -> Submenu:
        return self.repository.create(menu_id=menu_id, submenu_data=submenu_data)

    def update(self, menu_id: UUID, submenu_id: UUID, submenu_data: SubmenuInSchema) -> Submenu:
        return self.repository.update(menu_id=menu_id, submenu_id=submenu_id, submenu_data=submenu_data)

    def delete(self, menu_id: UUID, submenu_id: UUID) -> dict:
        return self.repository.delete(menu_id=menu_id, submenu_id=submenu_id)
