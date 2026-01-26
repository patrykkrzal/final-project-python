import pytest
from pydantic import ValidationError

from app.schemas import BookCreate, BookUpdate, UserCreate


class TestBookSchemas:
    def test_book_create_valid(self):
        book = BookCreate(
            title="Test Book",
            author="Test Author",
            year=2024,
            description="A test book",
        )
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.year == 2024

    def test_book_create_empty_title(self):
        with pytest.raises(ValidationError) as exc_info:
            BookCreate(title="   ", author="Author", year=2024)
        assert "title cannot be empty" in str(exc_info.value)

    def test_book_create_negative_year(self):
        with pytest.raises(ValidationError) as exc_info:
            BookCreate(title="Title", author="Author", year=-1)
        assert "year must be >= 0" in str(exc_info.value)

    def test_book_update_empty_title(self):
        with pytest.raises(ValidationError) as exc_info:
            BookUpdate(title="")
        assert "title cannot be empty" in str(exc_info.value)

    def test_book_update_negative_year(self):
        with pytest.raises(ValidationError) as exc_info:
            BookUpdate(year=-100)
        assert "year must be >= 0" in str(exc_info.value)


class TestUserSchemas:
    def test_user_create_valid(self):
        user = UserCreate(username="testuser", email="test@example.com", password="password123")
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_user_create_empty_username(self):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username="   ", email="test@example.com", password="password123")
        assert "username cannot be empty" in str(exc_info.value)

    def test_user_create_short_password(self):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username="user", email="test@example.com", password="short")
        assert "password must be at least 8 characters long" in str(exc_info.value)

    def test_user_create_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(username="user", email="not-an-email", password="password123")
