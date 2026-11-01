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
