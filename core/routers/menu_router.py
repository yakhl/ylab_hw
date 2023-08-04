from uuid import UUID

from fastapi import APIRouter, Depends

from ..schemas.menu_schemas import MenuInSchema, MenuOutSchema
from ..services.menu_service import MenuService

router = APIRouter(prefix='/menus')


@router.get('', response_model=list[MenuOutSchema])
def get_menus(menu: MenuService = Depends()):
    return menu.get_all()


@router.get('/{menu_id}', response_model=MenuOutSchema)
def get_menu(menu_id: UUID, menu: MenuService = Depends()):
    return menu.get(id=menu_id)


@router.post('', response_model=MenuOutSchema, status_code=201)
def create_menu(menu_data: MenuInSchema, menu: MenuService = Depends()):
    return menu.create(menu_data=menu_data)


@router.patch('/{menu_id}', response_model=MenuOutSchema)
def update_menu(menu_id: UUID, menu_data: MenuInSchema, menu: MenuService = Depends()):
    return menu.update(id=menu_id, menu_data=menu_data)


@router.delete('/{menu_id}', response_model=dict)
def delete_menu(menu_id: UUID, menu: MenuService = Depends()):
    return menu.delete(id=menu_id)
