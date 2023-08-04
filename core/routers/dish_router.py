from uuid import UUID

from fastapi import APIRouter, Depends

from ..schemas.dish_schemas import DishInSchema, DishOutSchema
from ..services.dish_service import DishService

router = APIRouter(prefix='/dishes')


@router.get('', response_model=list[DishOutSchema])
def get_dishes(menu_id: UUID, submenu_id: UUID, dish: DishService = Depends()):
    return dish.get_all(menu_id=menu_id, submenu_id=submenu_id)


@router.get('/{dish_id}', response_model=DishOutSchema)
def get_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: DishService = Depends()):
    return dish.get(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)


@router.post('', response_model=DishOutSchema, status_code=201)
def create_dish(menu_id: UUID, submenu_id: UUID, dish_data: DishInSchema, dish: DishService = Depends()):
    return dish.create(menu_id=menu_id, submenu_id=submenu_id, dish_data=dish_data)


@router.patch('/{dish_id}', response_model=DishOutSchema)
def update_dish(
    menu_id: UUID,
    submenu_id: UUID,
    dish_id: UUID,
    dish_data: DishInSchema,
    dish: DishService = Depends(),
):
    return dish.update(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id, dish_data=dish_data)


@router.delete('/{dish_id}', response_model=dict)
def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: DishService = Depends()):
    return dish.delete(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
