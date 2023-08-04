from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, validator


class DishBaseSchema(BaseModel):
    title: str
    description: str
    price: Decimal


class DishInSchema(DishBaseSchema):
    ...


class DishOutSchema(DishBaseSchema):
    submenu_id: UUID
    id: UUID

    @validator('price')
    def round_price(cls, value):
        return Decimal(value).quantize(Decimal('.01'))

    class Config:
        from_attributes = True
