from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.models import Dish, Submenu
from ..schemas.submenu_schemas import SubmenuInSchema
from .error_messages import (
    menu_404_msg,
    submenu_200_deleted_msg,
    submenu_404_msg,
    submenu_409_msg,
)


class SubmenuRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.model = Submenu

    def get_all(self, menu_id: UUID) -> list[Submenu]:
        db_submenus = self.db.query(Submenu).filter(Submenu.menu_id == menu_id).all()
        return [add_dishes_counter(db_submenu, self.db) for db_submenu in db_submenus]

    def get(self, menu_id: UUID, submenu_id: UUID) -> Submenu:
        db_submenu = self.db.query(Submenu).filter(Submenu.menu_id == menu_id).filter(Submenu.id == submenu_id).first()
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=submenu_404_msg)
        return add_dishes_counter(db_submenu, self.db)

    def create(self, menu_id: UUID, submenu_data: SubmenuInSchema) -> Submenu:
        if self.db.query(Submenu).filter(Submenu.menu_id == menu_id).all() is None:
            raise HTTPException(status_code=404, detail=menu_404_msg)
        if self.db.query(Submenu).filter(Submenu.menu_id == menu_id).filter(Submenu.title == submenu_data.title).first():
            raise HTTPException(status_code=409, detail=submenu_409_msg)
        db_submenu = Submenu(menu_id=menu_id, **submenu_data.dict())
        self.db.add(db_submenu)
        self.db.commit()
        self.db.refresh(db_submenu)
        return add_dishes_counter(db_submenu, self.db)

    def update(self, menu_id: UUID, submenu_id: UUID, submenu_data: SubmenuInSchema) -> Submenu:
        db_submenu = self.db.query(Submenu).filter(Submenu.menu_id == menu_id).filter(Submenu.id == submenu_id).first()
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=submenu_404_msg)
        db_submenu_by_title = (
            self.db.query(Submenu).filter(Submenu.menu_id == menu_id).filter(
                Submenu.title == submenu_data.title).first()
        )
        if db_submenu_by_title and db_submenu_by_title.id != submenu_id:
            raise HTTPException(status_code=409, detail=submenu_409_msg)
        for key, value in submenu_data.dict().items():
            setattr(db_submenu, key, value)
        self.db.commit()
        self.db.refresh(db_submenu)
        return add_dishes_counter(db_submenu, self.db)

    def delete(self, menu_id: UUID, submenu_id: UUID) -> dict:
        db_submenu = self.db.query(Submenu).filter(Submenu.menu_id == menu_id).filter(Submenu.id == submenu_id).first()
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=submenu_404_msg)
        self.db.delete(db_submenu)
        self.db.commit()
        return {'status': True, 'message': submenu_200_deleted_msg}


def add_dishes_counter(submenu: Submenu, db: Session):
    return {
        'dishes_count': db.query(func.count(Dish.id)).filter(Dish.submenu_id == submenu.id).scalar(),
        **submenu.__dict__,
    }
