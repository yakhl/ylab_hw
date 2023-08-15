from uuid import UUID

from fastapi import APIRouter, Depends

from core.models.models import Submenu
from core.schemas.submenu_schemas import (
    SubmenuCreateSchema,
    SubmenuOutSchema,
    SubmenuUpdateSchema,
)
from core.services.submenu_service import SubmenuService

router = APIRouter(prefix='/submenus')


@router.get('', response_model=list[SubmenuOutSchema])
async def get_submenus(menu_id: UUID, submenu: SubmenuService = Depends()) -> list[Submenu]:
    return await submenu.get_all(menu_id=menu_id)


@router.get('/{submenu_id}', response_model=SubmenuOutSchema)
async def get_submenu(menu_id: UUID, submenu_id: UUID, submenu: SubmenuService = Depends()) -> Submenu:
    return await submenu.get(menu_id=menu_id, submenu_id=submenu_id)


@router.post('', response_model=SubmenuOutSchema, status_code=201)
async def create_submenu(menu_id: UUID, submenu_data: SubmenuCreateSchema, submenu: SubmenuService = Depends()) -> Submenu:
    return await submenu.create(menu_id=menu_id, submenu_data=submenu_data)


@router.patch('/{submenu_id}', response_model=SubmenuOutSchema)
async def update_submenu(
    menu_id: UUID, submenu_id: UUID, submenu_data: SubmenuUpdateSchema, submenu: SubmenuService = Depends()
) -> Submenu:
    return await submenu.update(menu_id=menu_id, submenu_id=submenu_id, submenu_data=submenu_data)


@router.delete('/{submenu_id}', response_model=dict)
async def delete_submenu(menu_id: UUID, submenu_id: UUID, submenu: SubmenuService = Depends()) -> dict:
    return await submenu.delete(menu_id=menu_id, submenu_id=submenu_id)
