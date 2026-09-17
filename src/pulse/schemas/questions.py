"""Pydantic schemas for questions."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, TypeAdapter, model_validator

from pulse.schemas.common import RequestSchema
from pulse.schemas.categories import CategoryBase, CategoryRead

QuestionText = Annotated[str, StringConstraints(min_length=3, max_length=255, strip_whitespace=True)]
QuestionID = Annotated[int, Field(ge=1)]


class QuestionBase(BaseModel):
    text: QuestionText


class QuestionCreate(QuestionBase, RequestSchema):
    category_id: QuestionID | None = None


class QuestionResponse(QuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: QuestionID
    category_id: QuestionID | None = None
    category: CategoryRead | None = None


class QuestionUpdate(RequestSchema):
    text: QuestionText | None = None
    category_id: QuestionID | None = None


    @model_validator(mode="after")
    def reject_null_text(self):
        if "text" in self.model_fields_set and self.text is None:
            raise ValueError("text must not be null")
        return self


QuestionRead = QuestionResponse

QuestionList = TypeAdapter(list[QuestionRead])
