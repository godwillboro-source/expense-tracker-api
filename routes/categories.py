from marshmallow import Schema, ValidationError, fields, validate
from sqlalchemy.exc import IntegrityError
from app import app
from helpers import error, get_json, login_required
from models import Category
from config import db 

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
category_schema = CategorySchema()

def own_category(user, category_id):
    return Category.query.filter_by(id=category_id, user_id=user.id).first()


@app.route("/categories", methods=["GET"])
@login_required
def list_categories(user):
    categories = Category.query.filter_by(user_id=user.id).order_by(Category.name).all()
    return category_schema.dump(categories, many=True), 200


@app.route("/categories", methods=["POST"])
@login_required
def create_category(user):
    try:
        data = category_schema.load(get_json())
    except ValidationError as err:
        return error("Validation failed.", 422, details=err.messages)
    category = Category(name=data["name"].strip(), user_id=user.id)
    db.session.add(category)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("You already have a category with that name.", 409)
    return category_schema.dump(category), 201

@app.route("/categories/<int:id>", methods=["PATCH"])
@login_required
def update_category(id, user):
    category = own_category(user, id)
    if category is None:
        return error("Category not found.", 404)
    try:
        data = category_schema.load(get_json(), partial=True)
    except ValidationError as err:
        return error("Validation failed.", 422, details=err.messages)
    if "name" in data:
        category.name = data["name"].strip()
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("You already have a category with that name.", 409)
    return category_schema.dump(category), 200
