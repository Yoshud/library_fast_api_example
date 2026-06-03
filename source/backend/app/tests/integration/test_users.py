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
