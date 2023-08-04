from uuid import UUID

from pydantic import BaseModel


class SubmenuBaseSchema(BaseModel):
    title: str
    description: str


class SubmenuInSchema(SubmenuBaseSchema):
    ...


class SubmenuOutSchema(SubmenuBaseSchema):
    menu_id: UUID
    id: UUID
    dishes_count: int = 0

    class Config:
        from_attributes = True
