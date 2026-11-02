import os
from functools import wraps

from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError


from config import bcrypt, db
from models import User, Category, Expense

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URI", "sqlite:///app.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

@app.route("/")
def home():
    return jsonify("Welcome to expense tracker API")

from routes import auth, categories, expenses

if __name__ == "__main__":
    app.run(port=5555, debug=True)
