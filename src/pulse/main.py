"""Project CLI using Flask's standard commands and options."""

from flask.cli import FlaskGroup

from pulse import create_app

main = FlaskGroup(name="pulse", create_app=create_app)
