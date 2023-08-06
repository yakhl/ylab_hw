from uuid import UUID

from fastapi import APIRouter, Depends

from ..schemas.submenu_schemas import SubmenuInSchema, SubmenuOutSchema
from ..services.submenu_service import SubmenuService

router = APIRouter(prefix='/submenus')


@router.get('', response_model=list[SubmenuOutSchema])
def get_submenus(menu_id: UUID, submenu: SubmenuService = Depends()) -> list[dict]:
    return submenu.get_all(menu_id=menu_id)


@router.get('/{submenu_id}', response_model=SubmenuOutSchema)
def get_submenu(menu_id: UUID, submenu_id: UUID, submenu: SubmenuService = Depends()) -> dict:
    return submenu.get(menu_id=menu_id, submenu_id=submenu_id)


@router.post('', response_model=SubmenuOutSchema, status_code=201)
def create_submenu(menu_id: UUID, submenu_data: SubmenuInSchema, submenu: SubmenuService = Depends()) -> dict:
    return submenu.create(menu_id=menu_id, submenu_data=submenu_data)


@router.patch('/{submenu_id}', response_model=SubmenuOutSchema)
def update_submenu(menu_id: UUID, submenu_id: UUID, submenu_data: SubmenuInSchema, submenu: SubmenuService = Depends()) -> dict:
    return submenu.update(menu_id=menu_id, submenu_id=submenu_id, submenu_data=submenu_data)


@router.delete('/{submenu_id}', response_model=dict)
def delete_submenu(menu_id: UUID, submenu_id: UUID, submenu: SubmenuService = Depends()) -> dict:
    return submenu.delete(menu_id=menu_id, submenu_id=submenu_id)
