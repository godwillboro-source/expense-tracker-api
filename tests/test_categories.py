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