"""Question routes preserved from the prototype; operations are not implemented."""

from flask import Blueprint

questions_bp = Blueprint("questions", __name__, url_prefix="/questions")


def _not_implemented() -> tuple[dict[str, str], int]:
    return {"error": "Question operations are not implemented yet"}, 501


@questions_bp.route("", methods=["GET"])
def get_questions():
    return _not_implemented()


@questions_bp.route("", methods=["POST"])
def create_question():
    return _not_implemented()


@questions_bp.route("/<int:id>", methods=["DELETE"])
def delete_question(id: int):
    return _not_implemented()


@questions_bp.route("/<int:id>", methods=["PUT", "PATCH"])
def update_question(id: int):
    return _not_implemented()


@questions_bp.route("/<int:id>", methods=["GET"])
def get_question(id: int):
    return _not_implemented()
