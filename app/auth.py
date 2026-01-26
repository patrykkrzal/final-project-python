"""
Authentication helpers: password hashing/verification, JWT creation and token verification.
Note: behavior unchanged; added docstrings and minor formatting for clarity.
"""

import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- JWT / Auth settings ---
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "abc7d9f2e4k1m3n5p7q9r2s4t6v8w0x2z4")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def _truncate_bcrypt_limit(password: str) -> str:
    """Ensure password fits bcrypt ~72 bytes limit by safe UTF-8 truncation."""
    b = password.encode("utf-8")
    if len(b) > 72:
        b = b[:72]
    return b.decode("utf-8", errors="ignore")


def hash_password(password: str) -> str:
    """Hash plain password using passlib's bcrypt (safe-truncated)."""
    safe = _truncate_bcrypt_limit(password)
    try:
        return pwd_context.hash(safe)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Password hashing failed: {str(e)}") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hash (safe-truncated before verify)."""
    safe = _truncate_bcrypt_limit(plain_password)
    try:
        return pwd_context.verify(safe, hashed_password)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT with an optional custom expiration delta."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> str | None:
    """Decode and validate token; return username (sub) or None on failure."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """FastAPI dependency returning the current username or raising 401."""
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token)
    if username is None:
        raise credential_exception
    return username


def authenticate_demo_user(username: str, password: str) -> str | None:
    """Fallback demo authenticator (admin/admin) kept for tests/back-compat."""
    if username != ADMIN_USERNAME:
        return None

    if password == ADMIN_PASSWORD:
        return username

    return None
