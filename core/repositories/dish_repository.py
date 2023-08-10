from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from ..configs.error_messages import dish_404_msg, dish_409_msg, submenu_404_msg
from ..database.db import get_db
from ..models.models import Dish, Submenu
from ..schemas.dish_schemas import DishInSchema
from .submenu_repository import SubmenuRepository


class DishRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.model = Dish
        self.submenu_repo = SubmenuRepository(db)

    def _get_dish(self, menu_id: UUID, **kwargs) -> Dish:
        db_dish = self.db.query(Dish).filter_by(**kwargs).join(Submenu).filter_by(menu_id=menu_id).first()
        return db_dish

    def get_all(self, menu_id: UUID, submenu_id: UUID) -> list[dict]:
        db_dishes = (
            self.db.query(Dish)
            .filter(Dish.submenu_id == submenu_id)
            .join(Submenu)
            .filter(Submenu.menu_id == menu_id)
            .all()
        )
        return [db_dish.__dict__ for db_dish in db_dishes]

    def get(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> dict:
        db_dish = self._get_dish(menu_id=menu_id, submenu_id=submenu_id, id=dish_id)
        if db_dish is None:
            raise HTTPException(status_code=404, detail=dish_404_msg)
        return db_dish.__dict__

    def create(self, menu_id: UUID, submenu_id: UUID, dish_data: DishInSchema) -> dict:
        db_submenu = self.submenu_repo._get_submenu(menu_id=menu_id, id=submenu_id)
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=submenu_404_msg)
        db_dish_by_title = self._get_dish(menu_id=menu_id, submenu_id=submenu_id, title=dish_data.title)
        if db_dish_by_title:
            raise HTTPException(status_code=409, detail=dish_409_msg)
        db_dish = Dish(submenu_id=submenu_id, **dish_data.model_dump())
        self.db.add(db_dish)
        self.db.commit()
        self.db.refresh(db_dish)
        return db_dish.__dict__

    def update(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data: DishInSchema) -> dict:
        db_dish = self._get_dish(menu_id=menu_id, submenu_id=submenu_id, id=dish_id)
        if db_dish is None:
            raise HTTPException(status_code=404, detail=dish_404_msg)
        db_dish_by_title = self._get_dish(menu_id=menu_id, submenu_id=submenu_id, title=dish_data.title)
        if db_dish_by_title:
            raise HTTPException(status_code=409, detail=dish_409_msg)
        for key, value in dish_data.model_dump().items():
            setattr(db_dish, key, value)
        self.db.commit()
        self.db.refresh(db_dish)
        return db_dish.__dict__

    def delete(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> None:
        db_dish = self._get_dish(menu_id=menu_id, submenu_id=submenu_id, id=dish_id)
        if db_dish is None:
            raise HTTPException(status_code=404, detail=dish_404_msg)
        self.db.delete(db_dish)
        self.db.commit()
        return
