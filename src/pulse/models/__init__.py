"""Persistence models registered in SQLAlchemy metadata."""

from pulse.extensions import db
from pulse.models.answer import Answer
from pulse.models.category import Category
from pulse.models.question import Question

__all__ = ["Answer", "Category", "Question", "db"]
