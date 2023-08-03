from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from .. import schemas
from ..crud import menu_crud, submenu_crud
from ..db import get_db
from .error_messages import menu_404_msg, submenu_404_msg


router = APIRouter()


@router.get("/api/v1/menus/{menu_id}/submenus", response_model=list[schemas.SubmenuOut])
def read_submenus(menu_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # is it secure?
    # db_menu = menu_crud.get_menu(db, menu_id=menu_id)
    # if db_menu is None:
    #     raise HTTPException(status_code=404, detail=menu_crud.menu_router)
    submenus = submenu_crud.get_submenus(db=db, menu_id=menu_id, skip=skip, limit=limit)
    result = [
        {
            "dishes_count": submenu_crud.count_dishes_in_submenu(db=db, submenu_id=submenu.id),
            **submenu.__dict__,
        }
        for submenu in submenus
    ]
    return result


@router.get("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.SubmenuOut)
def read_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    db_submenu = submenu_crud.get_submenu(db=db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    return {
        "dishes_count": submenu_crud.count_dishes_in_submenu(db=db, submenu_id=submenu_id),
        **db_submenu.__dict__,
    }


@router.post(
    "/api/v1/menus/{menu_id}/submenus",
    response_model=schemas.SubmenuOut,
    status_code=201,
)
def create_submenu(menu_id: UUID, submenu: schemas.SubmenuIn, db: Session = Depends(get_db)):
    db_menu = menu_crud.get_menu(db=db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=404, detail=menu_404_msg)
    db_submenu = submenu_crud.get_submenu_by_title(
        db=db, menu_id=menu_id, submenu_title=submenu.title
    )
    if db_submenu:
        raise HTTPException(
            status_code=409,
            detail="Another submenu with this title already exists in the menu.",
        )
    return submenu_crud.post_submenu(db=db, menu_id=menu_id, submenu=submenu)


@router.patch("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=schemas.SubmenuOut)
def update_submenu(
    menu_id: UUID,
    submenu_id: UUID,
    new_submenu: schemas.SubmenuIn,
    db: Session = Depends(get_db),
):
    db_submenu = submenu_crud.get_submenu(db=db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    db_submenu_by_title = submenu_crud.get_submenu_by_title(
        db=db, menu_id=menu_id, submenu_title=new_submenu.title
    )
    if db_submenu_by_title and db_submenu_by_title.id != submenu_id:
        raise HTTPException(
            status_code=409,
            detail="Another submenu with this title already exists in the menu.",
        )
    changed_submenu = submenu_crud.change_submenu(
        db=db, submenu=db_submenu, new_submenu=new_submenu
    )
    return {
        "dishes_count": submenu_crud.count_dishes_in_submenu(db=db, submenu_id=changed_submenu.id),
        **changed_submenu.__dict__,
    }


@router.delete("/api/v1/menus/{menu_id}/submenus/{submenu_id}", response_model=dict)
def delete_submenu(menu_id: UUID, submenu_id: UUID, db: Session = Depends(get_db)):
    db_submenu = submenu_crud.get_submenu(db=db, menu_id=menu_id, submenu_id=submenu_id)
    if db_submenu is None:
        raise HTTPException(status_code=404, detail=submenu_404_msg)
    submenu_crud.remove_submenu(db=db, submenu=db_submenu)
    return {"status": True, "message": "The submenu has been deleted"}
