"""
SQLAlchemy models for the application.
Behavior unchanged; comments/docstrings added for clarity.
"""

from sqlalchemy import Column, Integer, String, UniqueConstraint

from .database import Base


class Book(Base):
    """Book entity stored in the 'books' table."""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    year = Column(Integer, nullable=True)


class User(Base):
    """User entity for authentication (no plain passwords stored)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email", name="uq_users_email"),
    )
