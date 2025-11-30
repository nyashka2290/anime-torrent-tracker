from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TorrentCreate(BaseModel):
    title: str | None = None
    description: str | None = None


class TorrentResponse(BaseModel):
    id: int
    info_hash: str
    title: str
    description: str | None
    size: int
    uploader_id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
