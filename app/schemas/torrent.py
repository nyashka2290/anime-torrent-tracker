from pydantic import BaseModel, ConfigDict

class TorrentBase(BaseModel):
    title: str | None = None
    description: str | None = None

class TorrentCreate(TorrentBase):
    pass

class TorrentResponse(TorrentBase):
    id: int
    info_hash: str
    size: int
    uploader_id: int

    model_config = ConfigDict(from_attributes=True)
