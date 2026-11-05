from tests.conftest import signup


def test_expense_crud(client):
    signup(client, "kim")
    res = client.post("/expenses", json={"title": "Lunch", "amount": 12.5})
    assert res.status_code == 201
    eid = res.json["id"]

    res = client.patch(f"/expenses/{eid}", json={"amount": 15})
    assert res.status_code == 200 and res.json["amount"] == 15
    assert res.json["title"] == "Lunch"

    assert client.get(f"/expenses/{eid}").status_code == 200
    assert client.delete(f"/expenses/{eid}").status_code == 204
    assert client.get(f"/expenses/{eid}").status_code == 404


def test_expense_validation(client):
    signup(client, "kim")
    assert client.post("/expenses", json={"title": "x", "amount": -5}).status_code == 422
    assert client.post("/expenses", json={"amount": 5}).status_code == 422


def test_pagination(client):
    signup(client, "kim")
    for i in range(25):
        client.post("/expenses", json={"title": f"e{i}", "amount": 1 + i})
    res = client.get("/expenses?page=3&per_page=10").json
    assert len(res["items"]) == 5
    assert res["total"] == 25 and res["pages"] == 3
    assert client.get("/expenses?page=abc").status_code == 400


def test_list_expenses_in_category(client):
    signup(client, "kim")
    food = client.post("/categories", json={"name": "Food"}).json
    travel = client.post("/categories", json={"name": "Travel"}).json

    food_expense = client.post(
        "/expenses",
        json={"title": "Lunch", "amount": 12.5, "category_id": food["id"]},
    ).json
    client.post(
        "/expenses",
        json={"title": "Train", "amount": 20, "category_id": travel["id"]},
    )
    client.post("/expenses", json={"title": "Coffee", "amount": 3})

    response = client.get(f"/categories/{food['id']}/expenses")
    assert response.status_code == 200
    assert response.json["total"] == 1
    assert response.json["items"] == [food_expense]


def test_users_cannot_touch_each_others_expenses(client, other_client):
    signup(client, "alice")
    signup(other_client, "bob")
    exp = client.post("/expenses", json={"title": "Secret", "amount": 9}).json

    assert other_client.get("/expenses").json["total"] == 0
    assert other_client.get(f"/expenses/{exp['id']}").status_code == 404
    assert other_client.patch(f"/expenses/{exp['id']}", json={"title": "hacked"}).status_code == 404
    assert other_client.delete(f"/expenses/{exp['id']}").status_code == 404
    assert client.get(f"/expenses/{exp['id']}").json["title"] == "Secret"


def test_cannot_use_someone_elses_category(client, other_client):
    signup(client, "alice")
    signup(other_client, "bob")
    cat = client.post("/categories", json={"name": "Food"}).json
    res = other_client.post("/expenses", json={"title": "x", "amount": 1, "category_id": cat["id"]})
    assert res.status_code == 422
    assert other_client.get(f"/categories/{cat['id']}/expenses").status_code == 404
    assert client.get("/categories/999/expenses").status_code == 404