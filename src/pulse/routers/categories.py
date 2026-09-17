"""CRUD routes for categories."""

from flask import Blueprint, abort, jsonify, request
from sqlalchemy import select

from pulse.models import Category, Question, db
from pulse.routers.common import configure_errors
from pulse.schemas import CategoryCreate, CategoryList, CategoryRead, CategoryUpdate

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")
configure_errors(categories_bp)


@categories_bp.get("")
def get_categories():
    records = db.session.scalars(select(Category).order_by(Category.id))
    return jsonify(CategoryList.dump_python(CategoryList.validate_python(records), mode="json"))


@categories_bp.post("")
def create_category():
    payload = CategoryCreate.model_validate(request.get_json())
    if db.session.get(Question, payload.question_id) is None:
        abort(404, description="Question not found")
    if db.session.scalar(select(Category.id).where(Category.question_id == payload.question_id)) is not None:
        abort(409, description="Question already has a category")
    record = Category(**payload.model_dump())
    db.session.add(record)
    db.session.commit()
    return jsonify(CategoryRead.model_validate(record).model_dump(mode="json")), 201


@categories_bp.get("/<int:id>")
def get_category(id: int):
    record = db.session.get(Category, id)
    if record is None:
        abort(404, description="Category not found")
    return jsonify(CategoryRead.model_validate(record).model_dump(mode="json"))


@categories_bp.route("/<int:id>", methods=["PUT", "PATCH"])
def update_category(id: int):
    record = db.session.get(Category, id)
    if record is None:
        abort(404, description="Category not found")
    schema = CategoryCreate if request.method == "PUT" else CategoryUpdate
    payload = schema.model_validate(request.get_json())
    changes = payload.model_dump(exclude_unset=True)
    if "question_id" in changes and db.session.get(Question, changes["question_id"]) is None:
        abort(404, description="Question not found")
    if "question_id" in changes and db.session.scalar(
        select(Category.id).where(Category.question_id == changes["question_id"], Category.id != id)
    ) is not None:
        abort(409, description="Question already has a category")
    for name, value in changes.items():
        setattr(record, name, value)
    db.session.commit()
    return jsonify(CategoryRead.model_validate(record).model_dump(mode="json"))


@categories_bp.delete("/<int:id>")
def delete_category(id: int):
    record = db.session.get(Category, id)
    if record is None:
        abort(404, description="Category not found")
    db.session.delete(record)
    db.session.commit()
    return "", 204
