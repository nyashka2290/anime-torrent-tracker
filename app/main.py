from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.v1.router import api_router
from app.db.session import AsyncSessionLocal
from app.models.torrent import Torrent

app = FastAPI(title="Anime Tracker")

# Подключаем статику (CSS, JS, картинки)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Настраиваем шаблоны
templates = Jinja2Templates(directory="app/templates")

# Подключаем API
app.include_router(api_router, prefix="/api/v1")

# --- Страницы сайта ---

@app.get("/")
async def index(request: Request):
    """Главная страница: показывает список торрентов"""
    async with AsyncSessionLocal() as db:
        query = (
            select(Torrent)
            .options(joinedload(Torrent.uploader))
            .order_by(Torrent.id.desc())
        )
        result = await db.execute(query)
        torrents = result.scalars().all()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "torrents": torrents}
    )

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/upload")
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})