from pydantic import BaseModel, ConfigDict, field_validator, EmailStr


class BookBase(BaseModel):
    title: str
    author: str
    description: str | None = None
    year: int | None = None


class BookCreate(BookBase):
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
    id: int

    model_config = ConfigDict(from_attributes=True)


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
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
    id: int
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
