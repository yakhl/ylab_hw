from uuid import UUID

from fastapi import APIRouter, Depends

from core.models.models import Menu
from core.schemas.menu_schemas import MenuCreateSchema, MenuOutSchema, MenuUpdateSchema
from core.schemas.response_schemas import Menu404, MenuDel200, MenuId409, MenuTitle409
from core.services.menu_service import MenuService

router = APIRouter(prefix='/menus', tags=['Меню'])


@router.get('', response_model=list[MenuOutSchema], summary='Получить список меню')
async def get_menus(menu: MenuService = Depends()) -> list[Menu]:
    """Получить список всех меню."""
    return await menu.get_all()


@router.get(
    '/{menu_id}',
    response_model=MenuOutSchema,
    responses={404: {'model': Menu404}},
    summary='Получить информацию о меню',
)
async def get_menu(menu_id: UUID, menu: MenuService = Depends()) -> Menu:
    """Получить информацию о конкретном меню."""
    return await menu.get(id=menu_id)


@router.post(
    '',
    response_model=MenuOutSchema,
    status_code=201,
    responses={409: {'model': MenuTitle409 | MenuId409}},
    summary='Создать меню',
)
async def create_menu(menu_data: MenuCreateSchema, menu: MenuService = Depends()) -> Menu:
    """Создать новое меню."""
    return await menu.create(menu_data=menu_data)


@router.patch(
    '/{menu_id}',
    response_model=MenuOutSchema,
    responses={404: {'model': Menu404}, 409: {'model': MenuTitle409}},
    summary='Обновить меню',
)
async def update_menu(menu_id: UUID, menu_data: MenuUpdateSchema, menu: MenuService = Depends()) -> Menu:
    """Обновить информацию о меню."""
    return await menu.update(id=menu_id, menu_data=menu_data)


@router.delete('/{menu_id}', response_model=dict, responses={200: {'model': MenuDel200}}, summary='Удалить меню')
async def delete_menu(menu_id: UUID, menu: MenuService = Depends()) -> dict:
    """Удалить меню."""
    return await menu.delete(id=menu_id)
