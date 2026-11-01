from functools import wraps

from flask import request, session

from models import User, db


def error(message, status, **extra):
    return {"error": message, **extra}, status


def get_json():
    return request.get_json(silent=True) or {}


def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def login_required(view):
    """Return 401 unless a user is logged in; passes the user to the route."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return error("Unauthorized. Please log in.", 401)
        return view(*args, user=user, **kwargs)
    return wrapper