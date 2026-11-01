from conftest import signup

def test_category_crud(client):
    signup(client, "kim")
    res = client.post("/categories", json={"name": "Food"})
    assert res.status_code == 201
    cid = res.json["id"]
    assert client.get("/categories").json[0]["name"] == "Food"
    assert client.patch(f"/categories/{cid}", json={"name": "Meals"}).json["name"] == "Meals"
    assert client.delete(f"/categories/{cid}").status_code == 204
    assert client.get("/categories").json == []

def test_category_names_unique_per_user(client, other_client):
    signup(client, "alice")
    signup(other_client, "bob")
    assert client.post("/categories", json={"name": "Food"}).status_code == 201
    assert client.post("/categories", json={"name": "Food"}).status_code == 409
    assert other_client.post("/categories", json={"name": "Food"}).status_code == 201

def test_users_cannot_touch_each_others_categories(client, other_client):
    signup(client, "alice")
    signup(other_client, "bob")
    cat = client.post("/categories", json={"name": "Food"}).json
    assert other_client.get("/categories").json == []
    assert other_client.patch(f"/categories/{cat['id']}", json={"name": "x"}).status_code == 404
    assert other_client.delete(f"/categories/{cat['id']}").status_code == 404

def test_deleting_category_keeps_expenses(client):
    signup(client, "kim")
    cat = client.post("/categories", json={"name": "Food"}).json
    exp = client.post("/expenses", json={"title": "x", "amount": 1, "category_id": cat["id"]}).json
    assert client.delete(f"/categories/{cat['id']}").status_code == 204
    assert client.get(f"/expenses/{exp['id']}").json["category_id"] is None