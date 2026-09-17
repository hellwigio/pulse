"""Pydantic schemas for answers."""

from pydantic import BaseModel, ConfigDict, TypeAdapter

from pulse.schemas.common import PartialUpdate, RequestSchema

from pulse.schemas.questions import QuestionID


class AnswerBase(BaseModel):
    is_agree: bool
    question_id: QuestionID


class AnswerCreate(AnswerBase, RequestSchema):
    pass


class AnswerRead(AnswerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class AnswerUpdate(PartialUpdate):
    is_agree: bool | None = None
    question_id: QuestionID | None = None


AnswerList = TypeAdapter(list[AnswerRead])
