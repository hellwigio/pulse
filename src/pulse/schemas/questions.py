"""Pydantic schemas for questions."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, TypeAdapter

from pulse.schemas.common import PartialUpdate, RequestSchema

QuestionText = Annotated[str, StringConstraints(min_length=3, max_length=255, strip_whitespace=True)]
QuestionID = Annotated[int, Field(ge=1)]


class QuestionBase(BaseModel):
    text: QuestionText


class QuestionCreate(QuestionBase, RequestSchema):
    pass


class QuestionRead(QuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: QuestionID


class QuestionUpdate(PartialUpdate):
    text: QuestionText | None = None


QuestionList = TypeAdapter(list[QuestionRead])
