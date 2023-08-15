from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MenuBaseSchema(BaseModel):
    title: str
    description: str


class MenuCreateSchema(MenuBaseSchema):
    id: UUID | None = None


class MenuUpdateSchema(MenuBaseSchema):
    ...


class MenuOutSchema(MenuBaseSchema):
    id: UUID
    submenus_count: int = 0
    dishes_count: int = 0

    model_config = ConfigDict(from_attributes=True)
