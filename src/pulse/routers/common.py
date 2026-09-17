"""Consistent JSON errors and transaction handling for API blueprints."""

from flask import Blueprint, jsonify
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from pulse.models import db


def configure_errors(blueprint: Blueprint) -> None:
    @blueprint.errorhandler(ValidationError)
    def validation_error(error: ValidationError):
        return jsonify({"error": error.errors(include_context=False, include_input=False)}), 422

    @blueprint.errorhandler(HTTPException)
    def http_error(error: HTTPException):
        return jsonify({"error": error.description}), error.code or 500

    @blueprint.errorhandler(IntegrityError)
    def integrity_error(error: IntegrityError):
        db.session.rollback()
        return jsonify({"error": "Operation conflicts with related data"}), 409
