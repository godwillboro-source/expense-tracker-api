from flask import session
from marshmallow import Schema, ValidationError, fields, validate
from sqlalchemy.exc import IntegrityError

from app import app
from helpers import current_user, error, get_json
from models import User
from config import db


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    # load_only: accepted on input, never returned.
    password = fields.Str(
        required=True, load_only=True, validate=validate.Length(min=8, max=128)
    )


user_schema = UserSchema()


@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = user_schema.load(get_json())
    except ValidationError as err:
        return error("Validation failed.", 422, details=err.messages)

    user = User(username=data["username"])
    user.password_hash = data["password"]
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Username already taken.", 409)

    session["user_id"] = user.id
    return user_schema.dump(user), 201


@app.route("/login", methods=["POST"])
def login():
    data = get_json()
    username, password = data.get("username"), data.get("password")
    if not username or not password:
        return error("Username and password are required.", 422)

    user = User.query.filter_by(username=username).first()
    if user is None or not user.authenticate(password):
        return error("Invalid username or password.", 401)

    session["user_id"] = user.id
    return user_schema.dump(user), 200


@app.route("/logout", methods=["DELETE"])
def logout():
    session.clear()
    return "", 204


@app.route("/check_session", methods=["GET"])
def check_session():
    user = current_user()
    if user is None:
        return error("Not logged in.", 401)
    return user_schema.dump(user), 200
