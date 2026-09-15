from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from pulse.extensions import db

if TYPE_CHECKING:
    from pulse.models.answer import Answer
    from pulse.models.category import Category


class Question(db.Model):
    __tablename__ = 'questions'

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text:Mapped[str] = mapped_column(nullable=False)
    category_id:Mapped[int] = mapped_column(nullable=True)

    answers: Mapped[list[Answer]] = relationship('Answer', back_populates='question')

    category:Mapped[Category] = relationship('Category', back_populates='question')
