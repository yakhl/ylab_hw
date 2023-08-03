from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas


def get_menus(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Menu).offset(skip).limit(limit).all()


def get_menu(db: Session, menu_id: UUID):
    return db.query(models.Menu).get(menu_id)


def get_menu_by_title(db: Session, menu_title: str):
    return db.query(models.Menu).filter(models.Menu.title == menu_title).first()


def post_menu(db: Session, menu: schemas.MenuIn):
    db_menu = models.Menu(**menu.dict())
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu


def change_menu(db: Session, menu: schemas.MenuOut, new_menu: schemas.MenuIn):
    for key, value in new_menu.dict().items():
        setattr(menu, key, value)
    db.commit()
    db.refresh(menu)
    return menu


def remove_menu(db: Session, menu: schemas.MenuOut):
    db.delete(menu)
    db.commit()
    return menu


def count_submenus_in_menu(db: Session, menu_id: UUID):
    return db.query(func.count(models.Submenu.id)).filter(models.Submenu.menu_id == menu_id).scalar()


def count_dishes_in_menu(db: Session, menu_id: UUID):
    return db.query(func.count(models.Dish.id)).join(models.Submenu).filter(models.Submenu.menu_id == menu_id).scalar()
