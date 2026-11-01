from flask import request
from marshmallow import Schema, ValidationError, fields, validate, validates

from app import app, db 
from helpers import error, get_json, login_required
from models import Category, Expense


class ExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    amount = fields.Float(required=True)
    date = fields.Date()  
    category_id = fields.Int(allow_none=True)

    @validates("amount")
    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError("Amount must be greater than 0.")


expense_schema = ExpenseSchema()


def own_expense(user, expense_id):
    return Expense.query.filter_by(id=expense_id, user_id=user.id).first()


def category_not_owned(user, category_id):
    """Return a 422 error if the category isn't the user's own, else None."""
    if category_id is None:
        return None
    if Category.query.filter_by(id=category_id, user_id=user.id).first() is None:
        return error("Validation failed.", 422, details={"category_id": ["Category not found."]})
    return None


@app.route("/expenses", methods=["GET"])
@login_required
def list_expenses(user):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return error("page and per_page must be integers.", 400)
    if page < 1 or per_page < 1:
        return error("page and per_page must be positive.", 400)

    pagination = (
        Expense.query.filter_by(user_id=user.id)
        .order_by(Expense.date.desc(), Expense.id.desc())
        .paginate(page=page, per_page=min(per_page, 100), error_out=False)
    )
    return {
        "items": expense_schema.dump(pagination.items, many=True),
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }, 200


@app.route("/expenses", methods=["POST"])
@login_required
def create_expense(user):
    try:
        data = expense_schema.load(get_json())
    except ValidationError as err:
        return error("Validation failed.", 422, details=err.messages)

    bad = category_not_owned(user, data.get("category_id"))
    if bad:
        return bad

    expense = Expense(**data, user_id=user.id)
    db.session.add(expense)
    db.session.commit()
    return expense_schema.dump(expense), 201


@app.route("/expenses/<int:id>", methods=["GET"])
@login_required
def get_expense(id, user):
    expense = own_expense(user, id)
    if expense is None:
        return error("Expense not found.", 404)
    return expense_schema.dump(expense), 200


@app.route("/expenses/<int:id>", methods=["PATCH"])
@login_required
def update_expense(id, user):
    expense = own_expense(user, id)
    if expense is None:
        return error("Expense not found.", 404)
    try:
        data = expense_schema.load(get_json(), partial=True)
    except ValidationError as err:
        return error("Validation failed.", 422, details=err.messages)

    if "category_id" in data:
        bad = category_not_owned(user, data["category_id"])
        if bad:
            return bad

    for field, value in data.items():
        setattr(expense, field, value)
    db.session.commit()
    return expense_schema.dump(expense), 200


@app.route("/expenses/<int:id>", methods=["DELETE"])
@login_required
def delete_expense(id, user):
    expense = own_expense(user, id)
    if expense is None:
        return error("Expense not found.", 404)
    db.session.delete(expense)
    db.session.commit()
    return "", 204