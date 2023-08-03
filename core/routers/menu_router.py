from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from .. import schemas
from ..crud import menu_crud
from ..db import get_db
from .error_messages import menu_404_msg


router = APIRouter()


@router.get("/api/v1/menus", response_model=list[schemas.MenuOut])
def read_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    menus = menu_crud.get_menus(db=db, skip=skip, limit=limit)
    return [
        {
            "submenus_count": menu_crud.count_submenus_in_menu(db=db, menu_id=menu.id),
            "dishes_count": menu_crud.count_dishes_in_menu(db=db, menu_id=menu.id),
            **menu.__dict__,
        }
        for menu in menus
    ]


@router.get("/api/v1/menus/{menu_id}", response_model=schemas.MenuOut)
def read_menu(menu_id: UUID, db: Session = Depends(get_db)):
    db_menu = menu_crud.get_menu(db=db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail=menu_404_msg)
    return {
        "submenus_count": menu_crud.count_submenus_in_menu(db=db, menu_id=menu_id),
        "dishes_count": menu_crud.count_dishes_in_menu(db=db, menu_id=db_menu.id),
        **db_menu.__dict__,
    }


@router.post("/api/v1/menus", response_model=schemas.MenuOut, status_code=201)
def create_menu(menu: schemas.MenuIn, db: Session = Depends(get_db)):
    db_menu = menu_crud.get_menu_by_title(db=db, menu_title=menu.title)
    if db_menu:
        raise HTTPException(status_code=409, detail="Another menu with this title already exists.")
    return menu_crud.post_menu(db=db, menu=menu)


@router.patch("/api/v1/menus/{menu_id}", response_model=schemas.MenuOut)
def update_menu(menu_id: UUID, new_menu: schemas.MenuIn, db: Session = Depends(get_db)):
    db_menu = menu_crud.get_menu(db=db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail=menu_404_msg)
    db_menu_by_title = menu_crud.get_menu_by_title(db=db, menu_title=new_menu.title)
    if db_menu_by_title and db_menu_by_title.id != menu_id:
        raise HTTPException(status_code=409, detail="Another menu with this title already exists.")
    changed_menu = menu_crud.change_menu(db=db, menu=db_menu, new_menu=new_menu)
    return {
        "submenus_count": menu_crud.count_submenus_in_menu(db=db, menu_id=changed_menu.id),
        "dishes_count": menu_crud.count_dishes_in_menu(db=db, menu_id=changed_menu.id),
        **changed_menu.__dict__,
    }


@router.delete("/api/v1/menus/{menu_id}", response_model=dict)
def delete_menu(menu_id: UUID, db: Session = Depends(get_db)):
    db_menu = menu_crud.get_menu(db=db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail=menu_404_msg)
    menu_crud.remove_menu(db=db, menu=db_menu)
    return {"status": True, "message": "The menu has been deleted"}
