"""Pydantic schemas for categories."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, TypeAdapter

from pulse.schemas.common import PartialUpdate, RequestSchema

from pulse.schemas.questions import QuestionID

CategoryName = Annotated[str, StringConstraints(min_length=1, max_length=255, strip_whitespace=True)]


class CategoryBase(BaseModel):
    name: CategoryName
    question_id: QuestionID


class CategoryCreate(CategoryBase, RequestSchema):
    pass


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CategoryUpdate(PartialUpdate):
    name: CategoryName | None = None
    question_id: QuestionID | None = None


CategoryList = TypeAdapter(list[CategoryRead])
