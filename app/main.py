from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload

from app.api.v1.router import api_router
from app.db.session import AsyncSessionLocal
from app.models.torrent import Torrent

app = FastAPI(title="Anime Tracker")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def index(request: Request, q: str = Query(None)):
    """Главная страница: показывает список торрентов"""
    async with AsyncSessionLocal() as db:
        query = select(Torrent).options(joinedload(Torrent.uploader))

        if q:
            search = f"%{q}%"
            query = query.where(
                or_(
                    Torrent.title.ilike(search),
                    Torrent.description.ilike(search)
                )
            )

        query = query.order_by(Torrent.id.desc())
        result = await db.execute(query)
        torrents = result.scalars().all()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "torrents": torrents, "search_query": q or ""}
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