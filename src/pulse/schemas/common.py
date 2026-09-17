"""Shared request validation."""

from pydantic import BaseModel, ConfigDict, model_validator


class RequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PartialUpdate(RequestSchema):
    @model_validator(mode="after")
    def reject_null_fields(self):
        for name in self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} must not be null")
        return self
