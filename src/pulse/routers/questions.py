"""CRUD routes for questions."""

from flask import Blueprint, abort, jsonify, request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from pulse.models import Answer, Category, Question, db
from pulse.routers.common import configure_errors
from pulse.schemas import QuestionCreate, QuestionList, QuestionRead, QuestionUpdate

questions_bp = Blueprint("questions", __name__, url_prefix="/questions")
configure_errors(questions_bp)


@questions_bp.get("")
def get_questions():
    records = db.session.scalars(select(Question).options(selectinload(Question.category)).order_by(Question.id))
    return jsonify(QuestionList.dump_python(QuestionList.validate_python(records), mode="json"))


@questions_bp.post("")
def create_question():
    payload = QuestionCreate.model_validate(request.get_json())
    if payload.category_id is not None and db.session.get(Category, payload.category_id) is None:
        abort(404, description="Category not found")
    record = Question(**payload.model_dump())
    db.session.add(record)
    db.session.commit()
    return jsonify(QuestionRead.model_validate(record).model_dump(mode="json")), 201


@questions_bp.get("/<int:id>")
def get_question(id: int):
    record = db.session.get(Question, id)
    if record is None:
        abort(404, description="Question not found")
    return jsonify(QuestionRead.model_validate(record).model_dump(mode="json"))


@questions_bp.route("/<int:id>", methods=["PUT", "PATCH"])
def update_question(id: int):
    record = db.session.get(Question, id)
    if record is None:
        abort(404, description="Question not found")
    schema = QuestionCreate if request.method == "PUT" else QuestionUpdate
    payload = schema.model_validate(request.get_json())
    changes = payload.model_dump(exclude_unset=request.method != "PUT")
    if changes.get("category_id") is not None and db.session.get(Category, changes["category_id"]) is None:
        abort(404, description="Category not found")
    for name, value in changes.items():
        setattr(record, name, value)
    db.session.commit()
    return jsonify(QuestionRead.model_validate(record).model_dump(mode="json"))


@questions_bp.delete("/<int:id>")
def delete_question(id: int):
    record = db.session.get(Question, id)
    if record is None:
        abort(404, description="Question not found")
    has_answers = db.session.scalar(select(Answer.id).where(Answer.question_id == id).limit(1))
    if has_answers is not None:
        abort(409, description="Delete related answers first")
    db.session.delete(record)
    db.session.commit()
    return "", 204
