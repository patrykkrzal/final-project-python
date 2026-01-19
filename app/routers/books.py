from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
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
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
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


@router.get("/{id}", response_model=schemas.Book)
def get_book(id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch("/{id}", response_model=schemas.Book)
def update_book(
    id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    book = db.query(models.Book).filter(models.Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{id}", status_code=204)
def delete_book(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    book = db.query(models.Book).filter(models.Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return None
