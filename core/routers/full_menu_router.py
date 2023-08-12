from fastapi import APIRouter, Depends

from ..schemas.full_menu_schema import Menu
from ..services.full_menu_service import FullMenuService

router = APIRouter(prefix='/full_menu')


@router.get('', response_model=list[Menu])
async def get_full_menu(full_menu: FullMenuService = Depends()) -> list[Menu]:
    return await full_menu.get()
