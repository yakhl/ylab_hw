from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal


class MenuBase(BaseModel):
    title: str
    description: str


class MenuIn(MenuBase):
    ...


class MenuOut(MenuBase):
    id: UUID
    submenus_count: int = 0
    dishes_count: int = 0

    class Config:
        orm_mode = True


class SubmenuBase(BaseModel):
    title: str
    description: str


class SubmenuIn(SubmenuBase):
    ...


class SubmenuOut(SubmenuBase):
    menu_id: UUID
    id: UUID
    dishes_count: int = 0

    class Config:
        orm_mode = True


class DishBase(BaseModel):
    title: str
    description: str
    price: Decimal


class DishIn(DishBase):
    ...


class DishOut(DishBase):
    submenu_id: UUID
    id: UUID

    class Config:
        orm_mode = True
