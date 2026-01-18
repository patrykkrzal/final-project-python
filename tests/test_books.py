from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_book():
    """Test POST /books/ with all fields"""
    response = client.post(
        "/books/",
        json={
            "title": "Test Book",
            "author": "Test Author",
            "description": "A test book description",
            "year": 2024,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"
    assert data["year"] == 2024


def test_create_book_minimal():
    """Test POST /books/ with only required fields"""
    response = client.post(
        "/books/",
        json={
            "title": "Minimal Book",
            "author": "Minimal Author",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal Book"
    assert data["author"] == "Minimal Author"
    assert data["description"] is None
    assert data["year"] is None


def test_create_book_validation_empty_title():
    """Test POST /books/ with empty title"""
    response = client.post(
        "/books/",
        json={
            "title": "",
            "author": "Test Author",
        },
    )
    assert response.status_code == 422


def test_create_book_validation_negative_year():
    """Test POST /books/ with negative year"""
    response = client.post(
        "/books/",
        json={
            "title": "Test Book",
            "author": "Test Author",
            "year": -5,
        },
    )
    assert response.status_code == 422


def test_get_book_by_id():
    """Test GET /books/{id}"""
    create_response = client.post(
        "/books/",
        json={
            "title": "Book to Get",
            "author": "Get Author",
            "year": 2023,
        },
    )
    assert create_response.status_code == 201
    book_id = create_response.json()["id"]
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "Book to Get"
    assert data["author"] == "Get Author"


def test_get_book_not_found():
    """Test GET /books/{id} with non-existent id"""
    response = client.get("/books/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_update_book():
    """Test PATCH /books/{id}"""
    create_response = client.post(
        "/books/",
        json={
            "title": "Original Title",
            "author": "Original Author",
            "year": 2020,
        },
    )
    assert create_response.status_code == 201
    book_id = create_response.json()["id"]

    update_response = client.patch(
        f"/books/{book_id}",
        json={
            "title": "Updated Title",
            "year": 2025,
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Original Author"
    assert data["year"] == 2025


def test_update_book_not_found():
    """Test PATCH /books/{id} with non-existent id - should return 404"""
    response = client.patch(
        "/books/999999",
        json={"title": "New Title"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_delete_book():
    """Test DELETE /books/{id} - deletes a book and returns 204"""
    create_response = client.post(
        "/books/",
        json={
            "title": "Book to Delete",
            "author": "Delete Author",
        },
    )
    assert create_response.status_code == 201
    book_id = create_response.json()["id"]

    delete_response = client.delete(f"/books/{book_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404


def test_delete_book_not_found():
    """Test DELETE /books/{id} with non-existent id"""
    response = client.delete("/books/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_list_books():
    """Test GET /books/ - lists all books"""
    response = client.get("/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
