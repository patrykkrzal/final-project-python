from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import SessionLocal

router = APIRouter(prefix="/books", tags=["books"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[schemas.Book])
def list_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()


@router.post("/", response_model=schemas.Book, status_code=201)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    # ensure required fields present (pydantic will normally validate)
    if not book.title or not book.author:
        raise HTTPException(status_code=400, detail="title and author are required")

    obj = models.Book(
        title=book.title,
        author=book.author,
        description=book.description,
        year=book.year,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
