from datetime import date

import pytest
from flask import Flask

from extensions import bcrypt, db
from models import Category, Expense, User


@pytest.fixture
def app_context():
    test_app = Flask(__name__)
    test_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite://",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY="test",
    )
    db.init_app(test_app)
    bcrypt.init_app(test_app)

    with test_app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


def create_user():
    user = User(username="test-user")
    user.password_hash = "test-password"
    db.session.add(user)
    db.session.commit()
    return user


def test_expense_is_saved_with_user_and_category(app_context):
    user = create_user()
    category = Category(name="Food", user=user)
    expense = Expense(
        title="Lunch",
        amount=12.5,
        date=date(2026, 11, 1),
        user=user,
        category=category,
    )
    db.session.add(expense)
    db.session.commit()

    saved_expense = db.session.get(Expense, expense.id)

    assert saved_expense is not None
    assert saved_expense.title == "Lunch"
    assert saved_expense.amount == 12.5
    assert saved_expense.date == date(2026, 11, 1)
    assert saved_expense.user.username == "test-user"
    assert saved_expense.category.name == "Food"


def test_expense_can_be_saved_without_category(app_context):
    user = create_user()
    expense = Expense(
        title="Bus fare",
        amount=2.0,
        date=date(2026, 11, 1),
        user=user,
    )
    db.session.add(expense)
    db.session.commit()

    saved_expense = db.session.get(Expense, expense.id)

    assert saved_expense is not None
    assert saved_expense.user_id == user.id
    assert saved_expense.category_id is None
    assert saved_expense.category is None
