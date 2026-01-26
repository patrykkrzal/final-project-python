import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_home_page():
    """Test that / returns the home page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_login_page():
    """Test that /login returns the login page."""
    response = client.get("/login")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_register_page():
    """Test that /register returns the register page."""
    response = client.get("/register")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_books_ui_page():
    """Test that /books/ui returns the books UI page."""
    response = client.get("/books/ui")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_add_book_page():
    """Test that /books/add returns the add book page."""
    response = client.get("/books/add")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_manage_books_page():
    """Test that /books/manage returns the manage books page."""
    response = client.get("/books/manage")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
