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


from datetime import date

from config import bcrypt, db
from sqlalchemy import MetaData
from sqlalchemy.ext.hybrid import hybrid_property

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)

    categories = db.relationship(
        "Category", back_populates="user", cascade="all, delete-orphan"
    )
    expenses = db.relationship(
        "Expense", back_populates="user", cascade="all, delete-orphan"
    )

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f"<User {self.id} {self.username}>"


class Category(db.Model):
    __tablename__ = "categories"
    # Category names are unique per user, not globally.
    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_category_user_name"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="categories")
    # Deleting a category keeps its expenses; their category_id becomes NULL.
    expenses = db.relationship("Expense", back_populates="category")

    def __repr__(self):
        return f"<Category {self.id} {self.name}>"


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    user = db.relationship("User", back_populates="expenses")
    category = db.relationship("Category", back_populates="expenses")

    def __repr__(self):
        return f"<Expense {self.id} {self.title} {self.amount}>"
