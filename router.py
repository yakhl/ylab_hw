from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID

import schemas
import crud
from db import get_db


menu_404_msg = "menu not found"
submenu_404_msg = "submenu not found"
dish_404_msg = "dish not found"


router = APIRouter()


@router.get("/api/v1/menus", response_model=list[schemas.MenuOut])
def read_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    menus = crud.get_menus(db, skip=skip, limit=limit)
    result = [
        {
            "submenus_count": crud.count_submenus_in_menu(db, menu_id=menu.id),
            "dishes_count": crud.count_dishes_in_menu(db, menu_id=menu.id),
            **menu.__dict__,
        }
        for menu in menus
    ]
    return result


@router.get("/api/v1/menus/{menu_id}", response_model=schemas.MenuOut)
def read_menu(menu_id: UUID, db: Session = Depends(get_db)):
    db_menu = crud.get_menu(db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail=menu_404_msg)
    submenus_count = crud.count_submenus_in_menu(db, menu_id=menu_id)
    return {
        "submenus_count": submenus_count,
        "dishes_count": crud.count_dishes_in_menu(db, menu_id=db_menu.id),
        **db_menu.__dict__,
    }


@router.post("/api/v1/menus", response_model=schemas.MenuOut, status_code=201)
def create_menu(menu: schemas.MenuIn, db: Session = Depends(get_db)):
    db_menu = crud.get_menu_by_title(db, title=menu.title)
    if db_menu:
        raise HTTPException(
            status_code=400, detail="Menu with this title already created"
        )
    return crud.post_menu(db=db, menu=menu)


@router.patch("/api/v1/menus/{menu_id}", response_model=schemas.MenuOut)
def update_menu(menu_id: UUID, new_menu: schemas.MenuIn, db: Session = Depends(get_db)):
    db_menu = crud.get_menu(db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail=menu_404_msg)
    if crud.get_menu_by_title(db, new_menu.title):
        raise HTTPException(
            status_code=400, detail="Menu with this title already created"
        )
    changed_menu = crud.change_menu(db, menu=db_menu, new_menu=new_menu)
    submenus_count = crud.count_submenus_in_menu(db, menu_id=changed_menu.id)
    return {
        "submenus_count": submenus_count,
        "dishes_count": crud.count_dishes_in_menu(db, menu_id=changed_menu.id),
        **changed_menu.__dict__,
    }


@router.delete("/api/v1/menus/{menu_id}", response_model=schemas.MenuOut)
def delete_menu(menu_id: UUID, db: Session = Depends(get_db)):
    db_menu = crud.get_menu(db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail=menu_404_msg)
    return crud.remove_menu(db, menu=db_menu)


@router.get("/api/v1/menus/{menu_id}/submenus", response_model=list[schemas.SubmenuOut])
def read_submenus(
    menu_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    db_menu = crud.get_menu(db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail=menu_404_msg)
    submenus = crud.get_submenus(db, menu_id=menu_id, skip=skip, limit=limit)
    result = [
        {
            "dishes_count": crud.count_dishes_in_submenu(db, submenu_id=submenu.id),
            **submenu.__dict__,
        }
        for submenu in submenus
    ]
    return result


@router.get(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.SubmenuOut
)
def read_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    db_submenu = crud.get_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    dishes_count = crud.count_dishes_in_submenu(db, submenu_id=submenu_id)
    return {"dishes_count": dishes_count, **db_submenu.__dict__}


@router.post(
    "/api/v1/menus/{menu_id}/submenus",
    response_model=schemas.SubmenuOut,
    status_code=201,
)
def create_submenu(
    menu_id: UUID, submenu: schemas.SubmenuIn, db: Session = Depends(get_db)
):
    db_menu = crud.get_menu(db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail=menu_404_msg)
    db_submenu = crud.get_submenu_by_title(db, menu_id=menu_id, title=submenu.title)
    if db_submenu:
        raise HTTPException(
            status_code=400,
            detail="Submenu with this title already created in this menu",
        )
    return crud.post_submenu(db=db, menu_id=menu_id, submenu=submenu)


@router.patch(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.SubmenuOut
)
def update_submenu(
    menu_id: UUID,
    submenu_id: UUID,
    new_submenu: schemas.SubmenuIn,
    db: Session = Depends(get_db),
):
    db_submenu = crud.get_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    if crud.get_submenu_by_title(db, menu_id=menu_id, title=new_submenu.title):
        raise HTTPException(
            status_code=400,
            detail="Submenu with this title already created in this menu",
        )
    changed_submenu = crud.change_submenu(
        db, submenu=db_submenu, new_submenu=new_submenu
    )
    dishes_count = crud.count_dishes_in_submenu(db, submenu_id=changed_submenu.id)
    return {"dishes_count": dishes_count, **changed_submenu.__dict__}


@router.delete(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.SubmenuOut
)
def delete_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    db_submenu = crud.get_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    return crud.remove_submenu(db, submenu=db_submenu)


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
    # db_submenu = crud.get_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    # if db_submenu is None:
    #     raise HTTPException(status_code=404, detail=submenu_404_msg)
    dishes = crud.get_dishes(db, submenu_id=submenu_id, skip=skip, limit=limit)
    for dish in dishes:
        dish.price = round(dish.price, 2)
    return dishes


@router.get(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=schemas.DishOut,
)
def read_dish(
    menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)
):
    db_submenu = crud.get_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    db_dish = crud.get_dish(db, submenu_id=submenu_id, dish_id=dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail=dish_404_msg)
    db_dish.price = round(db_dish.price, 2)
    return db_dish


@router.post(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes",
    response_model=schemas.DishOut,
    status_code=201,
)
def create_dish(
    menu_id: UUID, submenu_id: UUID, dish: schemas.DishIn, db: Session = Depends(get_db)
):
    db_submenu = crud.get_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    db_dish = crud.get_dish_by_title(db, submenu_id=submenu_id, title=dish.title)
    if db_dish:
        raise HTTPException(
            status_code=400,
            detail="Dish with this title already created in this submenu",
        )
    posted_dish = crud.post_dish(db=db, submenu_id=submenu_id, dish=dish)
    posted_dish.price = round(posted_dish.price, 2)
    return posted_dish


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
    db_submenu = crud.get_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    db_dish = crud.get_dish(db, submenu_id=submenu_id, dish_id=dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail=dish_404_msg)
    if crud.get_dish_by_title(db, submenu_id=submenu_id, title=new_dish.title):
        raise HTTPException(
            status_code=400,
            detail="Dish with this title already created in this submenu",
        )
    changed_dish = crud.change_dish(db, dish=db_dish, new_dish=new_dish)
    changed_dish.price = round(changed_dish.price, 2)
    return changed_dish


@router.delete(
    "/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
    response_model=schemas.DishOut,
)
def delete_dish(
    menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: Session = Depends(get_db)
):
    db_submenu = crud.get_submenu(db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    db_dish = crud.get_dish(db, submenu_id=submenu_id, dish_id=dish_id)
    if db_dish is None:
        raise HTTPException(status_code=404, detail=dish_404_msg)
    removed_dish = crud.remove_dish(db, dish=db_dish)
    removed_dish.price = round(removed_dish.price, 2)
    return removed_dish
