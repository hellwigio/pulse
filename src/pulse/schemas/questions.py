"""Pydantic schemas for questions."""

from pydantic import BaseModel


class Question(BaseModel):
    """Question schema; fields will be defined with the API contract."""

