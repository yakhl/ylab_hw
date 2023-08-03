from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, validator


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
        from_attributes = True


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
        from_attributes = True


class DishBase(BaseModel):
    title: str
    description: str
    price: Decimal


class DishIn(DishBase):
    ...


class DishOut(DishBase):
    submenu_id: UUID
    id: UUID

    @validator('price')
    def round_price(cls, value):
        return Decimal(value).quantize(Decimal('.01'))

    class Config:
        from_attributes = True
