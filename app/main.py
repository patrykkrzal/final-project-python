from fastapi import FastAPI, Request
from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import books
from app.database import Base, engine
import os

# Create tables at startup (SQLite/Postgres will create if needed)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LibraryLite")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
static_dir = str(BASE_DIR / "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(books.router)


@app.on_event("startup")
async def startup_event():
    from app.init_db import init_db
    init_db()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    # when running directly, reference module path explicitly
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
