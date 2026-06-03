async def test_get_user_list_empty(client):
    response = await client.get(
        "/api/users/",
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_get_user_not_existing(client):
    response = await client.get(
        "/api/users/000000",
    )
    assert response.status_code == 404


async def test_create_user(client):
    user_data = {"id": "100001", "name": "Test User"}
    response = await client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["id"] == "100001"
    assert response.json()["name"] == "Test User"


async def test_create_duplicate_user(client):
    user_data = {"id": "100002", "name": "Test User"}
    await client.post("/api/users/", json=user_data)

    response = await client.post("/api/users/", json=user_data)
    assert response.status_code == 409


async def test_get_existing_user(client):
    user_data = {"id": "100003", "name": "Existing User"}
    await client.post("/api/users/", json=user_data)

    response = await client.get("/api/users/100003")
    assert response.status_code == 200
    assert response.json()["id"] == "100003"
    assert response.json()["name"] == "Existing User"


async def test_get_user_list_with_data(client):
    user_data1 = {"id": "100010", "name": "User 10"}
    user_data2 = {"id": "100011", "name": "User 11"}
    await client.post("/api/users/", json=user_data1)
    await client.post("/api/users/", json=user_data2)

    response = await client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    ids = [u["id"] for u in data]
    assert "100010" in ids
    assert "100011" in ids


async def test_create_user_with_leading_zeros(client):
    user_data = {"id": "000011", "name": "Leading Zeros User"}
    response = await client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["id"] == "000011"

    get_response = await client.get("/api/users/000011")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == "000011"
