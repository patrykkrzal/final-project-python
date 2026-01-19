from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import Base, engine
from app.routers import books

# Create tables at startup (SQLite/Postgres will create if needed)
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.init_db import init_db

    init_db()
    yield
    # Shutdown (if needed in the future)


app = FastAPI(title="LibraryLite", lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
static_dir = str(BASE_DIR / "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(books.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    # when running directly, reference module path explicitly
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
