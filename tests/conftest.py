import os
import sys

os.environ["DATABASE_URI"] = "sqlite://"  # in-memory DB for tests
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest

from app import app as flask_app
from config import db


@pytest.fixture()
def app():
    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def other_client(app):
    """A second, independent browser session."""
    return app.test_client()


def signup(client, username, password="password123"):
    return client.post("/signup", json={"username": username, "password": password})