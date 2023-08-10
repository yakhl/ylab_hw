from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..configs.error_messages import menu_404_msg, submenu_404_msg, submenu_409_msg
from ..database.db import get_db
from ..models.models import Dish, Submenu
from ..schemas.submenu_schemas import SubmenuInSchema
from .menu_repository import MenuRepository


class SubmenuRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.model = Submenu
        self.menu_repo = MenuRepository(db)

    def _add_dishes_counter(self, submenu: Submenu) -> dict:
        return {
            'dishes_count': self.db.query(func.count(Dish.id)).filter(Dish.submenu_id == submenu.id).scalar(),
            **submenu.__dict__,
        }

    def _get_submenu(self, **kwargs) -> Submenu:
        db_submenu = self.db.query(Submenu).filter_by(**kwargs).first()
        return db_submenu

    def get_all(self, menu_id: UUID) -> list[dict]:
        db_submenus = self.db.query(Submenu).filter(Submenu.menu_id == menu_id).all()
        return [self._add_dishes_counter(db_submenu) for db_submenu in db_submenus]

    def get(self, menu_id: UUID, submenu_id: UUID) -> dict:
        db_submenu = self._get_submenu(menu_id=menu_id, id=submenu_id)
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=submenu_404_msg)
        return self._add_dishes_counter(db_submenu)

    def create(self, menu_id: UUID, submenu_data: SubmenuInSchema) -> dict:
        if self.menu_repo._get_menu(id=menu_id) is None:
            raise HTTPException(status_code=404, detail=menu_404_msg)
        if self._get_submenu(menu_id=menu_id, title=submenu_data.title):
            raise HTTPException(status_code=409, detail=submenu_409_msg)
        db_submenu = Submenu(menu_id=menu_id, **submenu_data.model_dump())
        self.db.add(db_submenu)
        self.db.commit()
        self.db.refresh(db_submenu)
        return self._add_dishes_counter(db_submenu)

    def update(self, menu_id: UUID, submenu_id: UUID, submenu_data: SubmenuInSchema) -> dict:
        db_submenu = self._get_submenu(menu_id=menu_id, id=submenu_id)
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=submenu_404_msg)
        db_submenu_by_title = self._get_submenu(menu_id=menu_id, title=submenu_data.title)
        if db_submenu_by_title and db_submenu_by_title.id != submenu_id:
            raise HTTPException(status_code=409, detail=submenu_409_msg)
        for key, value in submenu_data.model_dump().items():
            setattr(db_submenu, key, value)
        self.db.commit()
        self.db.refresh(db_submenu)
        return self._add_dishes_counter(db_submenu)

    def delete(self, menu_id: UUID, submenu_id: UUID) -> None:
        db_submenu = self._get_submenu(menu_id=menu_id, id=submenu_id)
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=submenu_404_msg)
        self.db.delete(db_submenu)
        self.db.commit()
        return
