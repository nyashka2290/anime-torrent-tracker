from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TorrentCreate(BaseModel):
    """Схема для создания торрента"""
    title: str | None = None
    description: str | None = None


class TorrentResponse(BaseModel):
    """Схема ответа с данными торрента"""
    id: int
    info_hash: str
    title: str
    description: str | None
    size: int
    uploader_id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
