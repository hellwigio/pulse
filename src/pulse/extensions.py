"""Flask extensions initialized by the application factory."""

from typing import TYPE_CHECKING

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()

# Flask-SQLAlchemy builds its model base dynamically; expose its type to checkers.
if TYPE_CHECKING:
    Model = Base
else:
    Model = db.Model
