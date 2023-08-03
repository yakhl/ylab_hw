from sqlalchemy.orm import Session
from uuid import UUID

from .. import models
from .. import schemas


def get_dishes(db: Session, submenu_id: UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Dish)
        .filter(models.Dish.submenu_id == submenu_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_dish(db: Session, menu_id: UUID, submenu_id: UUID, dish_id: UUID):
    return (
        db.query(models.Dish)
        .filter(models.Dish.id == dish_id, models.Dish.submenu_id == submenu_id)
        .join(models.Submenu)
        .filter(models.Submenu.menu_id == menu_id)
        .first()
    )


def get_dish_by_title(db: Session, submenu_id: UUID, dish_title: str):
    return (
        db.query(models.Dish)
        .filter(models.Dish.submenu_id == submenu_id)
        .filter(models.Dish.title == dish_title)
        .first()
    )


def post_dish(db: Session, submenu_id: UUID, dish: schemas.DishIn):
    db_dish = models.Dish(submenu_id=submenu_id, **dish.dict())
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


def change_dish(db: Session, dish: schemas.DishOut, new_dish: schemas.DishIn):
    for key, value in new_dish.dict().items():
        setattr(dish, key, value)
    db.commit()
    db.refresh(dish)
    return dish


def remove_dish(db: Session, dish: schemas.DishOut):
    db.delete(dish)
    db.commit()
    return dish
