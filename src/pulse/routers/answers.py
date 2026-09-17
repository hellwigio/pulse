"""CRUD routes for answers."""

from flask import Blueprint, abort, jsonify, request
from sqlalchemy import select

from pulse.models import Answer, Question, db
from pulse.routers.common import configure_errors
from pulse.schemas import AnswerCreate, AnswerList, AnswerRead, AnswerUpdate

answers_bp = Blueprint("answers", __name__, url_prefix="/answers")
configure_errors(answers_bp)


@answers_bp.get("")
def get_answers():
    records = db.session.scalars(select(Answer).order_by(Answer.id))
    return jsonify(AnswerList.dump_python(AnswerList.validate_python(records), mode="json"))


@answers_bp.post("")
def create_answer():
    payload = AnswerCreate.model_validate(request.get_json())
    if db.session.get(Question, payload.question_id) is None:
        abort(404, description="Question not found")
    record = Answer(**payload.model_dump())
    db.session.add(record)
    db.session.commit()
    return jsonify(AnswerRead.model_validate(record).model_dump(mode="json")), 201


@answers_bp.get("/<int:id>")
def get_answer(id: int):
    record = db.session.get(Answer, id)
    if record is None:
        abort(404, description="Answer not found")
    return jsonify(AnswerRead.model_validate(record).model_dump(mode="json"))


@answers_bp.route("/<int:id>", methods=["PUT", "PATCH"])
def update_answer(id: int):
    record = db.session.get(Answer, id)
    if record is None:
        abort(404, description="Answer not found")
    schema = AnswerCreate if request.method == "PUT" else AnswerUpdate
    payload = schema.model_validate(request.get_json())
    changes = payload.model_dump(exclude_unset=True)
    if "question_id" in changes and db.session.get(Question, changes["question_id"]) is None:
        abort(404, description="Question not found")
    for name, value in changes.items():
        setattr(record, name, value)
    db.session.commit()
    return jsonify(AnswerRead.model_validate(record).model_dump(mode="json"))


@answers_bp.delete("/<int:id>")
def delete_answer(id: int):
    record = db.session.get(Answer, id)
    if record is None:
        abort(404, description="Answer not found")
    db.session.delete(record)
    db.session.commit()
    return "", 204
