from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pulse.extensions import Model

if TYPE_CHECKING:
    from pulse.models.question import Question


class Category(Model):
    __tablename__ = 'categories'

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    name:Mapped[str] = mapped_column(nullable=False)

    question_id:Mapped[int] = mapped_column(ForeignKey('questions.id'))
    question:Mapped[Question] = relationship(
        'Question', back_populates='category', init=False, repr=False
    )
