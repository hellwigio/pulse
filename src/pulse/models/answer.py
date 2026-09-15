from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pulse.extensions import db

if TYPE_CHECKING:
    from pulse.models.question import Question


class Answer(db.Model):
    __tablename__ = 'answers'

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_agree:Mapped[bool] = mapped_column(nullable=False)
    question_id:Mapped[int] = mapped_column(ForeignKey('questions.id'))

    question:Mapped[Question] = relationship('Question', back_populates='answers')
