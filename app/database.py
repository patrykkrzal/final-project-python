"""
Database setup: engine/session configuration for SQLite/Postgres.
Behavior unchanged; docstring and comments added for clarity.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Prefer Settings.DATABASE_URL (from env). Fall back to local sqlite.
DATABASE_URL = settings.DATABASE_URL or os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Optional SSL flag for managed Postgres providers; disabled by default for local dev
REQUIRE_SSL = os.getenv("DATABASE_REQUIRE_SSL", "false").lower() == "true"

# If using Postgres and SSL is explicitly required but not present, append sslmode=require
if REQUIRE_SSL and DATABASE_URL.startswith("postgresql") and "sslmode" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
