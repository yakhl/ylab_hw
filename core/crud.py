from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from . import models
from . import schemas


def get_menus(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Menu).offset(skip).limit(limit).all()


def get_menu(db: Session, menu_id: UUID):
    return db.query(models.Menu).filter(models.Menu.id == menu_id).first()


def get_menu_by_title(db: Session, title: str):
    return db.query(models.Menu).filter(models.Menu.title == title).first()


def post_menu(db: Session, menu: schemas.MenuIn):
    db_menu = models.Menu(title=menu.title, description=menu.description)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu


def change_menu(db: Session, menu: schemas.MenuOut, new_menu: schemas.MenuIn):
    menu.title = new_menu.title
    menu.description = new_menu.description
    db.commit()
    db.refresh(menu)
    return menu


def remove_menu(db: Session, menu: schemas.MenuOut):
    db.delete(menu)
    db.commit()
    return menu


def get_submenus(db: Session, menu_id: UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Submenu)
        .filter(models.Submenu.menu_id == menu_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_submenu(db: Session, menu_id: UUID, submenu_id: UUID):
    return (
        db.query(models.Submenu)
        .filter(models.Submenu.menu_id == menu_id)
        .filter(models.Submenu.id == submenu_id)
        .first()
    )


def get_submenu_by_title(db: Session, menu_id: UUID, title: str):
    return (
        db.query(models.Submenu)
        .filter(models.Submenu.menu_id == menu_id)
        .filter(models.Submenu.title == title)
        .first()
    )


def post_submenu(db: Session, menu_id: UUID, submenu: schemas.SubmenuIn):
    db_submenu = models.Submenu(
        title=submenu.title, description=submenu.description, menu_id=menu_id
    )
    db.add(db_submenu)
    db.commit()
    db.refresh(db_submenu)
    return db_submenu


def change_submenu(
    db: Session, submenu: schemas.SubmenuOut, new_submenu: schemas.SubmenuIn
):
    submenu.title = new_submenu.title
    submenu.description = new_submenu.description
    db.commit()
    db.refresh(submenu)
    return submenu


def remove_submenu(db: Session, submenu: schemas.SubmenuOut):
    db.delete(submenu)
    db.commit()
    return submenu


def get_dishes(db: Session, submenu_id: UUID, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Dish)
        .filter(models.Dish.submenu_id == submenu_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_dish(db: Session, submenu_id: UUID, dish_id: UUID):
    return (
        db.query(models.Dish)
        .filter(models.Dish.submenu_id == submenu_id)
        .filter(models.Dish.id == dish_id)
        .first()
    )


def get_dish_by_title(db: Session, submenu_id: UUID, title: str):
    return (
        db.query(models.Dish)
        .filter(models.Dish.submenu_id == submenu_id)
        .filter(models.Dish.title == title)
        .first()
    )


def post_dish(db: Session, submenu_id: UUID, dish: schemas.DishIn):
    db_dish = models.Dish(
        title=dish.title,
        description=dish.description,
        price=dish.price,
        submenu_id=submenu_id,
    )
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


def change_dish(db: Session, dish: schemas.DishOut, new_dish: schemas.DishIn):
    dish.title = new_dish.title
    dish.description = new_dish.description
    dish.price = new_dish.price
    db.commit()
    db.refresh(dish)
    return dish


def remove_dish(db: Session, dish: schemas.DishOut):
    db.delete(dish)
    db.commit()
    return dish


def count_dishes_in_submenu(db: Session, submenu_id: UUID):
    return db.query(models.Dish).filter(models.Dish.submenu_id == submenu_id).count()


def count_submenus_in_menu(db: Session, menu_id: UUID):
    return db.query(models.Submenu).filter(models.Submenu.menu_id == menu_id).count()


def count_dishes_in_menu(db: Session, menu_id: UUID):
    submenus = db.query(models.Submenu).filter(models.Submenu.menu_id == menu_id).all()
    dishes_count = 0
    for submenu in submenus:
        dishes_count += count_dishes_in_submenu(db, submenu_id=submenu.id)
    return dishes_count
