from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from .. import schemas
from ..crud import submenu_crud, dish_crud
from ..db import get_db
from .error_messages import submenu_404_msg, dish_404_msg

router = APIRouter()


@router.get(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes",
    response_model=list[schemas.DishOut],
)
def read_dishes(
    menu_id: UUID,
    submenu_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    # postman test doesn't like this:
    # db_submenu = submenu_crud.get_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    # if db_submenu is None:
    #     raise HTTPException(status_code=404, detail=submenu_404_msg)
    return dish_crud.get_dishes(db=db, submenu_id=submenu_id, skip=skip, limit=limit)


@router.get(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=schemas.DishOut,
)
def read_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)):
    db_dish = dish_crud.get_dish(db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail=dish_404_msg)
    return db_dish


@router.post(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes",
    response_model=schemas.DishOut,
    status_code=201,
)
def create_dish(
    menu_id: UUID, submenu_id: UUID, dish: schemas.DishIn, db: Session = Depends(get_db)
):
    db_submenu = submenu_crud.get_submenu(db=db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    db_dish = dish_crud.get_dish_by_title(db=db, submenu_id=submenu_id, dish_title=dish.title)
    if db_dish:
        raise HTTPException(
            status_code=409,
            detail="Another dish with this title already exists in the submenu.",
        )
    return dish_crud.post_dish(db=db, submenu_id=submenu_id, dish=dish)


@router.patch(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=schemas.DishOut,
)
def update_dish(
    menu_id: UUID,
    submenu_id: UUID,
    dish_id: UUID,
    new_dish: schemas.DishIn,
    db: Session = Depends(get_db),
):
    db_dish = dish_crud.get_dish(db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail=dish_404_msg)
    dish_by_title = dish_crud.get_dish_by_title(
        db=db, submenu_id=submenu_id, dish_title=new_dish.title
    )
    if dish_by_title and dish_by_title.id != dish_id:
        raise HTTPException(
            status_code=409,
            detail="Another dish with this title already exists in the submenu.",
        )
    return dish_crud.change_dish(db=db, dish=db_dish, new_dish=new_dish)


@router.delete(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=dict,
)
def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)):
    db_dish = dish_crud.get_dish(db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail=dish_404_msg)
    dish_crud.remove_dish(db=db, dish=db_dish)
    return {"status": True, "message": "The dish has been deleted"}
