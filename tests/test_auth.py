import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestAuth:
    def test_login_success(self):
        response = client.post(
            "/auth/token",
            data={"username": "admin", "password": "admin"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_invalid_username(self):
        response = client.post(
            "/auth/token",
            data={"username": "wronguser", "password": "admin"},
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_invalid_password(self):
        response = client.post(
            "/auth/token",
            data={"username": "admin", "password": "wrongpass"},
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_get_current_user(self):
        login_response = client.post(
            "/auth/token",
            data={"username": "admin", "password": "admin"},
        )
        token = login_response.json()["access_token"]

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["username"] == "admin"

    def test_get_current_user_no_token(self):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self):
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        assert response.status_code == 401


class TestProtectedEndpoints:
    @pytest.fixture
    def auth_token(self):
        response = client.post(
            "/auth/token",
            data={"username": "admin", "password": "admin"},
        )
        return response.json()["access_token"]

    def test_create_book_without_auth(self):
        response = client.post(
            "/books/",
            json={"title": "Test Book", "author": "Test Author"},
        )
        assert response.status_code == 401

    def test_create_book_with_auth(self, auth_token):
        response = client.post(
            "/books/",
            json={"title": "Secure Book", "author": "Secure Author", "year": 2024},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Secure Book"
        assert "id" in response.json()

    def test_update_book_without_auth(self):
        response = client.patch(
            "/books/1",
            json={"title": "Updated"},
        )
        assert response.status_code == 401

    def test_delete_book_without_auth(self):
        response = client.delete("/books/1")
        assert response.status_code == 401

    def test_get_book_without_auth(self):
        auth_response = client.post(
            "/auth/token",
            data={"username": "admin", "password": "admin"},
        )
        token = auth_response.json()["access_token"]

        create_response = client.post(
            "/books/",
            json={"title": "Public Book", "author": "Author"},
            headers={"Authorization": f"Bearer {token}"},
        )
        book_id = create_response.json()["id"]

        get_response = client.get(f"/books/{book_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Public Book"


class TestListBooksPublic:
    def test_list_books_without_auth(self):
        response = client.get("/books/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAuthEdgeCases:
    def test_token_without_sub_claim(self):
        # Create token without 'sub' claim
        from app.auth import JWT_SECRET_KEY, JWT_ALGORITHM
        from jose import jwt
        from datetime import datetime, timedelta, timezone

        token_data = {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
        bad_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert response.status_code == 401

    def test_verify_password_exception_handling(self):
        # Test verify_password with corrupted hash returns False
        from app.auth import verify_password

        result = verify_password("test", "corrupted_hash")
        assert result is False

    def test_create_token_with_custom_expiry(self):
        # Test create_access_token with custom expires_delta
        from app.auth import create_access_token, verify_token
        from datetime import timedelta

        token = create_access_token(
            data={"sub": "testuser"}, expires_delta=timedelta(minutes=10)
        )
        username = verify_token(token)
        assert username == "testuser"

    def test_long_password_truncation(self):
        # Test password longer than 72 bytes (bcrypt limit)
        long_password = "a" * 100
        response = client.post(
            "/auth/token",
            data={"username": "admin", "password": long_password},
        )
        assert response.status_code == 401
