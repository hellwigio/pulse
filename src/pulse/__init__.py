"""Pulse application factory."""

import os

from flask import Flask

from pulse.config import DevelopmentConfig, ProductionConfig, TestingConfig
from pulse.extensions import db, migrate
from pulse.routers import register_blueprints

CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def create_app(config_object: object | None = None) -> Flask:
    app = Flask(__name__)

    if config_object is None:
        mode = os.environ.get("APP_ENV", "development")
        try:
            config_object = CONFIG_MAP[mode]
        except KeyError:
            raise ValueError(
                f"Unknown APP_ENV {mode!r}. Expected one of: {', '.join(CONFIG_MAP)}"
            ) from None

    app.config.from_object(config_object)

    db.init_app(app)
    # Import all models so Alembic can discover their tables in db.metadata.
    from pulse import models  # noqa: F401

    migrate.init_app(app, db)

    register_blueprints(app)

    return app
