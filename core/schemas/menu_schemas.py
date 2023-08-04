from uuid import UUID

from pydantic import BaseModel


class MenuBaseSchema(BaseModel):
    title: str
    description: str


class MenuInSchema(MenuBaseSchema):
    ...


class MenuOutSchema(MenuBaseSchema):
    id: UUID
    submenus_count: int = 0
    dishes_count: int = 0

    class Config:
        from_attributes = True
