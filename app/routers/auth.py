from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.auth import (
    JWT_EXPIRE_MINUTES,
    authenticate_demo_user,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: EmailStr  # ensures valid email format


class RegisterResponse(BaseModel):
    message: str
    username: str
    email: EmailStr


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_demo_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def read_current_user(current_user: str = Depends(get_current_user)):
    return {"username": current_user}


# Demo registration endpoint. In real app, persist user to DB and hash password.
@router.post("/register", response_model=RegisterResponse)
async def register(payload: RegisterRequest):
    # extra simple rule: email must contain '@' (redundant to EmailStr, but explicit per request)
    if "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Email must contain '@'")
    return RegisterResponse(
        message="Registered (demo, not persisted)",
        username=payload.username,
        email=payload.email,
    )
