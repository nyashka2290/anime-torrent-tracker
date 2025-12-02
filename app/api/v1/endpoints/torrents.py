from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.torrent import Torrent
from app.models.user import User
from app.schemas.torrent import TorrentCreate, TorrentResponse
from app.services.torrent_service import TorrentService

router = APIRouter()


@router.post("/upload", response_model=TorrentResponse)
async def upload_torrent(
        file: UploadFile = File(...),
        title: str | None = Form(None),
        description: str | None = Form(None),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
) -> Torrent:
    """Загрузка нового торрента (только для авторизованных)"""
    torrent_in = TorrentCreate(title=title, description=description)

    return await TorrentService.create_torrent(
        db=db,
        torrent_in=torrent_in,
        file=file,
        uploader_id=current_user.id
    )


@router.get("/", response_model=list[TorrentResponse])
async def read_torrents(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
) -> Any:
    """Получение списка торрентов (Доступно всем)"""
    query = select(Torrent).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{torrent_id}/download")
async def download_torrent(
        torrent_id: int,
        db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Скачивание торрента по ID"""
    query = select(Torrent).where(Torrent.id == torrent_id)
    result = await db.execute(query)
    torrent = result.scalar_one_or_none()

    if not torrent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Torrent not found"
        )

    if not Path(torrent.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Torrent file not found on disk"
        )

    return FileResponse(
        path=torrent.file_path,
        filename=f"{torrent.title}.torrent",
        media_type='application/x-bittorrent'
    )