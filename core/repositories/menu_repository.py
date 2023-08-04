from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.models import Dish, Menu, Submenu
from ..schemas.menu_schemas import MenuInSchema
from .error_messages import menu_200_deleted_msg, menu_404_msg, menu_409_msg


class MenuRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.model = Menu

    def get_all(self) -> list[Menu]:
        db_menus = self.db.query(Menu).all()
        return [add_counters(db_menu, self.db) for db_menu in db_menus]

    def get(self, id: UUID) -> Menu:
        db_menu = self.db.query(Menu).get(id)
        if db_menu is None:
            raise HTTPException(status_code=404, detail=menu_404_msg)
        return add_counters(db_menu, self.db)

    def create(self, menu_data: MenuInSchema) -> Menu:
        if self.db.query(Menu).filter(Menu.title == menu_data.title).first():
            raise HTTPException(status_code=409, detail=menu_409_msg)
        db_menu = Menu(**menu_data.dict())
        self.db.add(db_menu)
        self.db.commit()
        self.db.refresh(db_menu)
        return add_counters(db_menu, self.db)

    def update(self, id: UUID, menu_data: MenuInSchema) -> Menu:
        db_menu = self.db.query(Menu).get(id)
        if db_menu is None:
            raise HTTPException(status_code=404, detail=menu_404_msg)
        db_menu_by_title = self.db.query(Menu).filter(Menu.title == menu_data.title).first()
        if db_menu_by_title and db_menu_by_title.id != id:
            raise HTTPException(status_code=409, detail=menu_409_msg)
        for key, value in menu_data.dict().items():
            setattr(db_menu, key, value)
        self.db.commit()
        self.db.refresh(db_menu)
        return add_counters(db_menu, self.db)

    def delete(self, id: UUID) -> dict:
        db_menu = self.db.query(Menu).get(id)
        if db_menu is None:
            raise HTTPException(status_code=404, detail=menu_404_msg)
        self.db.delete(db_menu)
        self.db.commit()
        return {'status': True, 'message': menu_200_deleted_msg}


def add_counters(menu: Menu, db: Session):
    return {
        'submenus_count': db.query(func.count(Submenu.id)).filter(Submenu.menu_id == menu.id).scalar(),
        'dishes_count': db.query(func.count(Dish.id)).join(Submenu).filter(Submenu.menu_id == menu.id).scalar(),
        **menu.__dict__,
    }
