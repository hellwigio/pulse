"""Environment-based application configuration."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key")
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    pass
