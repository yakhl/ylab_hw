from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SubmenuBaseSchema(BaseModel):
    title: str
    description: str


class SubmenuCreateSchema(SubmenuBaseSchema):
    id: UUID | None = None


class SubmenuUpdateSchema(SubmenuBaseSchema):
    ...


class SubmenuOutSchema(SubmenuBaseSchema):
    menu_id: UUID
    id: UUID
    dishes_count: int = 0

    model_config = ConfigDict(from_attributes=True)
