from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas


def get_submenus(db: Session, menu_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Submenu).filter(models.Submenu.menu_id == menu_id).offset(skip).limit(limit).all()


def get_submenu(db: Session, menu_id: UUID, submenu_id: UUID):
    return (
        db.query(models.Submenu)
        .filter(models.Submenu.menu_id == menu_id)
        .filter(models.Submenu.id == submenu_id)
        .first()
    )


def get_submenu_by_title(db: Session, menu_id: UUID, submenu_title: str):
    return (
        db.query(models.Submenu)
        .filter(models.Submenu.menu_id == menu_id)
        .filter(models.Submenu.title == submenu_title)
        .first()
    )


def post_submenu(db: Session, menu_id: UUID, submenu: schemas.SubmenuIn):
    db_submenu = models.Submenu(menu_id=menu_id, **submenu.dict())
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


def change_submenu(db: Session, submenu: schemas.SubmenuOut, new_submenu: schemas.SubmenuIn):
    for key, value in new_submenu.dict().items():
        setattr(submenu, key, value)
    db.commit()
    db.refresh(submenu)
    return submenu


def remove_submenu(db: Session, submenu: schemas.SubmenuOut):
    db.delete(submenu)
    db.commit()
    return submenu


def count_dishes_in_submenu(db: Session, submenu_id: UUID):
    return db.query(func.count(models.Dish.id)).filter(models.Dish.submenu_id == submenu_id).scalar()
