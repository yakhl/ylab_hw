from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SubmenuBaseSchema(BaseModel):
    title: str
    description: str


class SubmenuInSchema(SubmenuBaseSchema):
    id: UUID | None = None


class SubmenuOutSchema(SubmenuBaseSchema):
    menu_id: UUID
    id: UUID
    dishes_count: int = 0

    model_config = ConfigDict(from_attributes=True)
