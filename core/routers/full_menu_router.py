from fastapi import APIRouter, Depends

from core.schemas.full_menu_schema import Menu
from core.services.full_menu_service import FullMenuService

router = APIRouter(prefix='/full_menu', tags=['Полное меню'])


@router.get('', response_model=list[Menu], summary='Получить полное меню')
async def get_full_menu(full_menu: FullMenuService = Depends()) -> list[Menu]:
    """Получить список всех меню с подменю и блюдами"""
    return await full_menu.get()
