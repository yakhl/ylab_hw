from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class DishBaseSchema(BaseModel):
    title: str
    description: str
    price: Decimal


class DishInSchema(DishBaseSchema):
    id: UUID | None = None


class DishOutSchema(DishBaseSchema):
    submenu_id: UUID
    id: UUID

    @field_validator('price')
    def round_price(cls, value) -> Decimal:
        return Decimal(value).quantize(Decimal('.01'))

    model_config = ConfigDict(from_attributes=True)
