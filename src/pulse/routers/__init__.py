"""HTTP blueprint registration."""

from flask import Flask

from pulse.routers.answers import answers_bp
from pulse.routers.categories import categories_bp
from pulse.routers.questions import questions_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(questions_bp)
    app.register_blueprint(answers_bp)
    app.register_blueprint(categories_bp)
