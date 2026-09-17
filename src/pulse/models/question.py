from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pulse.extensions import Model

if TYPE_CHECKING:
    from pulse.models.answer import Answer
    from pulse.models.category import Category


class Question(Model):
    __tablename__ = 'questions'

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    text:Mapped[str] = mapped_column(nullable=False)
    category_id:Mapped[int | None] = mapped_column(ForeignKey('categories.id'), nullable=True, default=None)

    answers: Mapped[list[Answer]] = relationship(
        'Answer', back_populates='question', init=False, repr=False
    )

    category:Mapped[Category | None] = relationship(
        'Category', back_populates='questions', init=False, repr=False
    )
