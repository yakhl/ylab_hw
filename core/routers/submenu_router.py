from uuid import UUID

from fastapi import APIRouter, Depends

from core.models.models import Submenu
from core.schemas.response_schemas import (
    Menu404,
    Submenu404,
    SubmenuDel200,
    SubmenuId409,
    SubmenuTitle409,
)
from core.schemas.submenu_schemas import (
    SubmenuCreateSchema,
    SubmenuOutSchema,
    SubmenuUpdateSchema,
)
from core.services.submenu_service import SubmenuService

router = APIRouter(prefix='/submenus', tags=['Подменю'])


@router.get('', response_model=list[SubmenuOutSchema], summary='Получить список подменю')
async def get_submenus(menu_id: UUID, submenu: SubmenuService = Depends()) -> list[Submenu]:
    """Получить список всех подменю в меню."""

    return await submenu.get_all(menu_id=menu_id)


@router.get(
    '/{submenu_id}',
    response_model=SubmenuOutSchema,
    responses={404: {'model': Submenu404}},
    summary='Получить информацию о подменю',
)
async def get_submenu(menu_id: UUID, submenu_id: UUID, submenu: SubmenuService = Depends()) -> Submenu:
    """Получить информацию о конкретном подменю в меню."""
    return await submenu.get(menu_id=menu_id, submenu_id=submenu_id)


@router.post(
    '',
    response_model=SubmenuOutSchema,
    status_code=201,
    responses={409: {'model': SubmenuTitle409 | SubmenuId409}, 404: {'model': Menu404}},
    summary='Создать подменю',
)
async def create_submenu(
    menu_id: UUID, submenu_data: SubmenuCreateSchema, submenu: SubmenuService = Depends()
) -> Submenu:
    """Создать новое подменю в меню."""
    return await submenu.create(menu_id=menu_id, submenu_data=submenu_data)


@router.patch(
    '/{submenu_id}',
    response_model=SubmenuOutSchema,
    responses={404: {'model': Submenu404}, 409: {'model': SubmenuTitle409}},
    summary='Обновить информацию о подменю',
)
async def update_submenu(
    menu_id: UUID, submenu_id: UUID, submenu_data: SubmenuUpdateSchema, submenu: SubmenuService = Depends()
) -> Submenu:
    """Обновить информацию о подменю в меню."""
    return await submenu.update(menu_id=menu_id, submenu_id=submenu_id, submenu_data=submenu_data)


@router.delete(
    '/{submenu_id}', response_model=dict, responses={200: {'model': SubmenuDel200}}, summary='Удалить подменю'
)
async def delete_submenu(menu_id: UUID, submenu_id: UUID, submenu: SubmenuService = Depends()) -> dict:
    """Удалить подменю из меню."""
    return await submenu.delete(menu_id=menu_id, submenu_id=submenu_id)
