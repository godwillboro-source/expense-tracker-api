from tests.conftest import signup
from models import User


def test_signup_logs_in_and_hides_password(client):
    res = signup(client, "kim")
    assert res.status_code == 201
    assert "password" not in res.json and "_password_hash" not in res.json
    assert client.get("/check_session").status_code == 200


def test_password_is_hashed(client, app):
    signup(client, "kim")
    user = User.query.filter_by(username="kim").first()
    assert user._password_hash != "password123"
    assert user.authenticate("password123")


def test_duplicate_username_409(client, other_client):
    signup(client, "kim")
    assert signup(other_client, "kim").status_code == 409


def test_signup_validation_422(client):
    assert signup(client, "kim", "short").status_code == 422


def test_login_logout_flow(client):
    signup(client, "kim")
    client.delete("/logout")
    assert client.get("/check_session").status_code == 401
    assert (
        client.post("/login", json={"username": "kim", "password": "wrong"}).status_code
        == 401
    )
    assert (
        client.post(
            "/login", json={"username": "kim", "password": "password123"}
        ).status_code
        == 200
    )


def test_resources_require_login(client):
    assert client.get("/expenses").status_code == 401
    assert client.post("/expenses", json={"title": "x", "amount": 1}).status_code == 401
    assert client.get("/categories").status_code == 401
    assert client.delete("/categories/1").status_code == 401
