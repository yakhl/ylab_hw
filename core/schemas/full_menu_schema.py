from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_validator


class Dish(BaseModel):
    type: str = 'DISH'
    id: UUID
    title: str
    description: str
    price: Decimal

    @field_validator('price')
    def round_price(cls, value) -> Decimal:
        return Decimal(value).quantize(Decimal('.01'))


class Submenu(BaseModel):
    type: str = 'SUBMENU'
    id: UUID
    title: str
    description: str
    dishes: list[Dish]


class Menu(BaseModel):
    type: str = 'MENU'
    id: UUID
    title: str
    description: str
    submenus: list[Submenu]
