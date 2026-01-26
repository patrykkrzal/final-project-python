"""
Pydantic schemas for Books and Users.
Behavior unchanged; added docstrings and minor comments to improve clarity.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class BookBase(BaseModel):
    """Common fields shared by Book variants."""

    title: str
    author: str
    description: str | None = None
    year: int | None = None


class BookCreate(BookBase):
    """Payload for creating a new book with validation."""

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title cannot be empty")
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("year must be >= 0")
        return v


class BookUpdate(BaseModel):
    """Partial update payload for an existing book."""

    title: str | None = None
    author: str | None = None
    description: str | None = None
    year: int | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            raise ValueError("title cannot be empty")
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("year must be >= 0")
        return v


class Book(BookBase):
    """Response schema for a stored book (includes id)."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# --- User schemas ---
class UserBase(BaseModel):
    """Fields common to all user representations (excluding password)."""

    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Payload for registering a new user (includes password)."""

    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("username cannot be empty")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or len(v) < 8:
            raise ValueError("password must be at least 8 characters long")
        return v


class UserRead(UserBase):
    """Response schema for a stored user (no password)."""

    id: int
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """OAuth2 password grant token response returned by /auth/token."""

    access_token: str
    token_type: str = "bearer"
