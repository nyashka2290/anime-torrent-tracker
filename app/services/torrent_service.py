from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from torrentool.api import Torrent as TorrentParser

from app.models.torrent import Torrent
from app.schemas.torrent import TorrentCreate

STORAGE_PATH = Path("storage/torrents")


class TorrentService:
    @staticmethod
    async def create_torrent(
            db: AsyncSession,
            torrent_in: TorrentCreate,
            file: UploadFile,
            uploader_id: int
    ) -> Torrent:
        file_bytes = await file.read()

        try:
            # Парсим .torrent файл
            torrent_meta = TorrentParser.from_string(file_bytes)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid .torrent file"
            )

        # Duplicate torrent check
        query = select(Torrent).where(Torrent.info_hash == torrent_meta.info_hash)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Torrent already exists"
            )

        file_name = f"{torrent_meta.info_hash}.torrent"
        file_path = STORAGE_PATH / file_name

        STORAGE_PATH.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Создаем запись в БД
        db_torrent = Torrent(
            info_hash=torrent_meta.info_hash,
            title=torrent_in.title or torrent_meta.name,  # Если юзер не дал имя, берем из файла
            description=torrent_in.description,
            size=torrent_meta.total_size,
            file_path=str(file_path),
            uploader_id=uploader_id
        )

        db.add(db_torrent)
        await db.commit()
        await db.refresh(db_torrent)

        return db_torrent