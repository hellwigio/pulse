"""HTTP blueprint registration."""

from flask import Flask

from pulse.routers.questions import questions_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(questions_bp)
