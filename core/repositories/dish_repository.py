from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.models import Dish, Submenu
from ..schemas.dish_schemas import DishInSchema
from .error_messages import dish_404_msg, dish_409_msg, submenu_404_msg


class DishRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.model = Dish

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
        db_dish = (
            self.db.query(Dish)
            .filter(Dish.id == dish_id, Dish.submenu_id == submenu_id)
            .join(Submenu)
            .filter(Submenu.menu_id == menu_id)
            .first()
        )
        if db_dish is None:
            raise HTTPException(status_code=404, detail=dish_404_msg)
        return db_dish.__dict__

    def create(self, menu_id: UUID, submenu_id: UUID, dish_data: DishInSchema) -> dict:
        db_submenu = self.db.query(Submenu).filter(Submenu.menu_id == menu_id).filter(Submenu.id == submenu_id).first()
        if db_submenu is None:
            raise HTTPException(status_code=404, detail=submenu_404_msg)
        db_dish_by_title = (
            self.db.query(Dish).filter(Dish.submenu_id == submenu_id).filter(Dish.title == dish_data.title).first()
        )
        if db_dish_by_title:
            raise HTTPException(status_code=409, detail=dish_409_msg)
        db_dish = Dish(submenu_id=submenu_id, **dish_data.dict())
        self.db.add(db_dish)
        self.db.commit()
        self.db.refresh(db_dish)
        return db_dish.__dict__

    def update(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data: DishInSchema) -> dict:
        db_dish = (
            self.db.query(Dish)
            .filter(Dish.id == dish_id, Dish.submenu_id == submenu_id)
            .join(Submenu)
            .filter(Submenu.menu_id == menu_id)
            .first()
        )
        if db_dish is None:
            raise HTTPException(status_code=404, detail=dish_404_msg)
        db_dish_by_title = (
            self.db.query(Dish).filter(Dish.submenu_id == submenu_id).filter(Dish.title == dish_data.title).first()
        )
        if db_dish_by_title and db_dish_by_title.id != dish_id:
            raise HTTPException(status_code=409, detail=dish_409_msg)
        for key, value in dish_data.dict().items():
            setattr(db_dish, key, value)
        self.db.commit()
        self.db.refresh(db_dish)
        return db_dish.__dict__

    def delete(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> None:
        db_dish = (
            self.db.query(Dish)
            .filter(Dish.id == dish_id, Dish.submenu_id == submenu_id)
            .join(Submenu)
            .filter(Submenu.menu_id == menu_id)
            .first()
        )
        if db_dish is None:
            raise HTTPException(status_code=404, detail=dish_404_msg)
        self.db.delete(db_dish)
        self.db.commit()
        return
