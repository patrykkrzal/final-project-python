from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import Base, engine
from app.routers import auth, books

# Create tables at startup (SQLite/Postgres will create if needed)
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.init_db import init_db

    init_db()
    yield


app = FastAPI(title="LibraryLite", lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
static_dir = str(BASE_DIR / "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


# added pages for auth
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


# IMPORTANT: define /books/ui before including books router to avoid /books/{id} catching it
@app.get("/books/ui")
def books_ui_page(request: Request):
    return templates.TemplateResponse(request, "books_ui.html")


@app.get("/books/add")
def add_book_page(request: Request):
    return templates.TemplateResponse(request, "add_book.html")


@app.get("/books/manage")
def manage_books_page(request: Request):
    return templates.TemplateResponse(request, "manage_books.html")


# include routers after specific pages
app.include_router(auth.router)
app.include_router(books.router)


if __name__ == "__main__":
    import uvicorn

    # when running directly, reference module path explicitly
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
