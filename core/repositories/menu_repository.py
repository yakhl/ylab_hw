from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..configs.error_messages import menu_404_msg, menu_409_msg
from ..database.db import get_db
from ..models.models import Dish, Menu, Submenu
from ..schemas.menu_schemas import MenuInSchema


class MenuRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.model = Menu

    def _add_counters(self, menu: Menu) -> dict:
        return {
            'submenus_count': self.db.query(func.count(Submenu.id)).filter(Submenu.menu_id == menu.id).scalar(),
            'dishes_count': self.db.query(func.count(Dish.id))
            .join(Submenu)
            .filter(Submenu.menu_id == menu.id)
            .scalar(),
            **menu.__dict__,
        }

    def _get_menu(self, **kwargs) -> Menu:
        db_menu = self.db.query(Menu).filter_by(**kwargs).first()
        return db_menu

    def get_all(self) -> list[dict]:
        db_menus = self.db.query(Menu).all()
        return [self._add_counters(db_menu) for db_menu in db_menus]

    def get(self, id: UUID) -> dict:
        db_menu = self._get_menu(id=id)
        if db_menu is None:
            raise HTTPException(status_code=404, detail=menu_404_msg)
        return self._add_counters(db_menu)

    def create(self, menu_data: MenuInSchema) -> dict:
        if self._get_menu(title=menu_data.title):
            raise HTTPException(status_code=409, detail=menu_409_msg)
        db_menu = Menu(**menu_data.dict())
        self.db.add(db_menu)
        self.db.commit()
        self.db.refresh(db_menu)
        return self._add_counters(db_menu)

    def update(self, id: UUID, menu_data: MenuInSchema) -> dict:
        db_menu = self._get_menu(id=id)
        if db_menu is None:
            raise HTTPException(status_code=404, detail=menu_404_msg)
        db_menu_by_title = self._get_menu(title=menu_data.title)
        if db_menu_by_title and db_menu_by_title.id != id:
            raise HTTPException(status_code=409, detail=menu_409_msg)
        for key, value in menu_data.dict().items():
            setattr(db_menu, key, value)
        self.db.commit()
        self.db.refresh(db_menu)
        return self._add_counters(db_menu)

    def delete(self, id: UUID) -> None:
        db_menu = self._get_menu(id=id)
        if db_menu is None:
            raise HTTPException(status_code=404, detail=menu_404_msg)
        self.db.delete(db_menu)
        self.db.commit()
        return
