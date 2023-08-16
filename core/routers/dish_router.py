from uuid import UUID

from fastapi import APIRouter, Depends

from core.models.models import Dish
from core.schemas.dish_schemas import DishCreateSchema, DishOutSchema, DishUpdateSchema
from core.schemas.response_schemas import (
    Dish404,
    DishDel200,
    DishId409,
    DishTitle409,
    Submenu404,
)
from core.services.dish_service import DishService

router = APIRouter(prefix='/dishes', tags=['Блюда'])


@router.get('', response_model=list[DishOutSchema], summary='Получить список блюд')
async def get_dishes(menu_id: UUID, submenu_id: UUID, dish: DishService = Depends()) -> list[Dish]:
    """Получить список всех блюд в подменю."""
    return await dish.get_all(menu_id=menu_id, submenu_id=submenu_id)


@router.get(
    '/{dish_id}',
    response_model=DishOutSchema,
    responses={404: {'model': Dish404}},
    summary='Получить информацию о блюде',
)
async def get_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: DishService = Depends()) -> Dish:
    """Получить информацию о конкретном блюде в подменю."""
    return await dish.get(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)


@router.post(
    '',
    response_model=DishOutSchema,
    status_code=201,
    responses={404: {'model': Submenu404}, 409: {'model': DishTitle409 | DishId409}},
    summary='Создать блюдо',
)
async def create_dish(
    menu_id: UUID, submenu_id: UUID, dish_data: DishCreateSchema, dish: DishService = Depends()
) -> Dish:
    """Создать новое блюдо в подменю."""
    return await dish.create(menu_id=menu_id, submenu_id=submenu_id, dish_data=dish_data)


@router.patch(
    '/{dish_id}',
    response_model=DishOutSchema,
    responses={404: {'model': Dish404}, 409: {'model': DishTitle409}},
    summary='Обновить информацию о блюде',
)
async def update_dish(
    menu_id: UUID,
    submenu_id: UUID,
    dish_id: UUID,
    dish_data: DishUpdateSchema,
    dish: DishService = Depends(),
) -> Dish:
    """Обновить информацию о блюде в подменю."""
    return await dish.update(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id, dish_data=dish_data)


@router.delete('/{dish_id}', response_model=dict, responses={200: {'model': DishDel200}}, summary='Удалить блюдо')
async def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: DishService = Depends()) -> dict:
    """Удалить блюдо из подменю."""
    return await dish.delete(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
