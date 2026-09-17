"""Pydantic schemas for categories."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, TypeAdapter

from pulse.schemas.common import PartialUpdate, RequestSchema


CategoryName = Annotated[str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)]


class CategoryBase(BaseModel):
    name: CategoryName


class CategoryCreate(CategoryBase, RequestSchema):
    pass


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CategoryUpdate(PartialUpdate):
    name: CategoryName | None = None


CategoryList = TypeAdapter(list[CategoryRead])
