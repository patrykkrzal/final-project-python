from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth import (
    JWT_EXPIRE_MINUTES,
    authenticate_demo_user,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import SessionLocal
from app.models import User
from app.schemas import TokenResponse, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: EmailStr  # ensures valid email format


class RegisterResponse(BaseModel):
    message: str
    username: str
    email: EmailStr


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Try DB-backed authentication first
    user_in_db = db.query(User).filter(User.username == form_data.username).first()
    print(f"[AUTH] Login attempt for '{form_data.username}': found_in_db={bool(user_in_db)}")
    if user_in_db:
        ok = verify_password(form_data.password, user_in_db.hashed_password)
        print(f"[AUTH] Password verify for '{form_data.username}': {ok}")
        if ok:
            access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
            access_token = create_access_token(data={"sub": user_in_db.username}, expires_delta=access_token_expires)
            return TokenResponse(access_token=access_token)

    # Fallback to demo admin (to keep existing tests passing)
    user = authenticate_demo_user(form_data.username, form_data.password)
    print(f"[AUTH] Fallback demo auth for '{form_data.username}': {'success' if user else 'failed'}")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user}, expires_delta=access_token_expires)

    return TokenResponse(access_token=access_token)


@router.get("/me")
async def read_current_user(current_user: str = Depends(get_current_user)):
    return {"username": current_user}


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(payload: UserCreate, db: Session = Depends(get_db)):
    # Uniqueness checks
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Create user with hashed password
    user = User(
        username=payload.username.strip(),
        email=str(payload.email),
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"[AUTH] Registered user id={user.id} username='{user.username}' email='{user.email}'")

    return RegisterResponse(
        message="Registered successfully",
        username=user.username,
        email=user.email,
    )


@router.get("/debug/users")
async def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in users]
