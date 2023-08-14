from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MenuBaseSchema(BaseModel):
    title: str
    description: str


class MenuInSchema(MenuBaseSchema):
    id: UUID | None = None


class MenuOutSchema(MenuBaseSchema):
    id: UUID
    submenus_count: int = 0
    dishes_count: int = 0

    model_config = ConfigDict(from_attributes=True)
