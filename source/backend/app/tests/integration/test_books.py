async def test_get_books_empty(client):
    response = await client.get("/api/books/")
    assert response.status_code == 200
    assert response.json() == []

async def test_get_book_not_existing(client):
    response = await client.get("/api/books/999999")
    assert response.status_code == 404

async def test_create_book_with_title(client):
    book_data = {
        "id": "200001",
        "book_title": {
            "title": "New Book",
            "author": "Author Name"
        }
    }
    response = await client.post("/api/books/", json=book_data)
    assert response.status_code == 201
    assert response.json()["id"] == "200001"
    assert "book_title_id" in response.json()

async def test_create_book_with_title_id(client):
    # First create a book to get a title id
    book_data1 = {
        "id": "200002",
        "book_title": {
            "title": "Existing Book",
            "author": "Existing Author"
        }
    }
    response1 = await client.post("/api/books/", json=book_data1)
    title_id = response1.json()["book_title_id"]

    # Now create second book using title_id
    book_data2 = {
        "id": "200003",
        "book_title_id": title_id
    }
    response2 = await client.post("/api/books/", json=book_data2)
    assert response2.status_code == 201
    assert response2.json()["id"] == "200003"
    assert response2.json()["book_title_id"] == title_id

async def test_create_book_duplicate_id(client):
    book_data = {
        "id": "200004",
        "book_title": {"title": "T", "author": "A"}
    }
    await client.post("/api/books/", json=book_data)
    response = await client.post("/api/books/", json=book_data)
    assert response.status_code == 409

async def test_update_borrowers(client):
    # Create user
    await client.post("/api/users/", json={"id": "100001", "name": "Borrower"})
    # Create book
    await client.post("/api/books/", json={"id": "200005", "book_title": {"title": "B", "author": "A"}})
    
    update_data = {
        "update_borrowers_map": {
            "200005": "100001"
        }
    }
    response = await client.put("/api/books/", json=update_data)
    assert response.status_code == 200
    
    # Check if borrowed
    get_resp = await client.get("/api/books/200005")
    assert get_resp.status_code == 200
    assert get_resp.json()["user"]["id"] == "100001"

    # Return book
    return_data = {
        "update_borrowers_map": {
            "200005": None
        }
    }
    response2 = await client.put("/api/books/", json=return_data)
    assert response2.status_code == 200

    get_resp2 = await client.get("/api/books/200005")
    assert get_resp2.status_code == 200
    assert get_resp2.json()["user"] is None

async def test_update_borrowers_already_borrowed(client):
    await client.post("/api/users/", json={"id": "100002", "name": "B1"})
    await client.post("/api/users/", json={"id": "100003", "name": "B2"})
    await client.post("/api/books/", json={"id": "200006", "book_title": {"title": "B", "author": "A"}})
    
    await client.put("/api/books/", json={"update_borrowers_map": {"200006": "100002"}})
    response = await client.put("/api/books/", json={"update_borrowers_map": {"200006": "100003"}})
    assert response.status_code == 409

async def test_update_borrowers_user_not_found(client):
    await client.post("/api/books/", json={"id": "200007", "book_title": {"title": "B", "author": "A"}})
    response = await client.put("/api/books/", json={"update_borrowers_map": {"200007": "999999"}})
    assert response.status_code == 404

async def test_update_borrowers_book_not_found(client):
    await client.post("/api/users/", json={"id": "100004", "name": "B1"})
    response = await client.put("/api/books/", json={"update_borrowers_map": {"888888": "100004"}})
    assert response.status_code == 404

async def test_bulk_update_borrowers_borrow_and_return(client):
    await client.post("/api/users/", json={"id": "100010", "name": "User 1"})
    await client.post("/api/users/", json={"id": "100011", "name": "User 2"})
    
    await client.post("/api/books/", json={"id": "200010", "book_title": {"title": "B1", "author": "A1"}})
    await client.post("/api/books/", json={"id": "200011", "book_title": {"title": "B2", "author": "A2"}})
    
    await client.put("/api/books/", json={"update_borrowers_map": {"200010": "100010"}})
    
    update_data = {
        "update_borrowers_map": {
            "200010": None,
            "200011": "100011"
        }
    }
    response = await client.put("/api/books/", json=update_data)
    assert response.status_code == 200
    
    book1_resp = await client.get("/api/books/200010")
    assert book1_resp.json()["user"] is None
    
    book2_resp = await client.get("/api/books/200011")
    assert book2_resp.json()["user"]["id"] == "100011"

async def test_bulk_update_borrowers_rollback_on_error(client):
    await client.post("/api/users/", json={"id": "100012", "name": "User 3"})
    await client.post("/api/books/", json={"id": "200012", "book_title": {"title": "B3", "author": "A3"}})
    
    book12_resp_initial = await client.get("/api/books/200012")
    assert book12_resp_initial.json()["user"] is None
    
    update_data = {
        "update_borrowers_map": {
            "200012": "100012",
            "999999": "100012"
        }
    }
    response = await client.put("/api/books/", json=update_data)
    assert response.status_code == 404
    
    book12_resp_after = await client.get("/api/books/200012")
    assert book12_resp_after.json()["user"] is None
