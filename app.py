import os

from flask import Flask
from flask_migrate import Migrate

from models import bcrypt, db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

# Route modules are imported last because they need `app` to exist.

import routes.auth


import routes.expenses

import routes.categories