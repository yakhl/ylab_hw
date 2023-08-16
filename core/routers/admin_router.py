from fastapi import APIRouter, Depends

from core.schemas.response_schemas import (
    Dish404,
    DishId409,
    DishTitle409,
    Menu404,
    MenuId409,
    MenuTitle409,
    Submenu404,
    SubmenuId409,
    SubmenuTitle409,
    SyncTableNoNeed200,
    SyncTableSuccess200,
)
from core.tasks.table import TableSync

router = APIRouter(prefix='/admin', tags=['Админка'])


@router.post(
    '/sync_table',
    response_model=dict,
    responses={
        200: {'model': SyncTableSuccess200 | SyncTableNoNeed200},
        409: {'model': MenuTitle409 | MenuId409 | SubmenuTitle409 | SubmenuId409 | DishTitle409 | DishId409},
        404: {'model': Menu404 | Submenu404 | Dish404},
    },
    summary='Обновить БД из админки',
)
async def sync_table_db(table: TableSync = Depends()) -> dict:
    """Обновить базу данных из админки"""
    return await table.sync_table()
