from sqlalchemy import String, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_class import Base


class Torrent(Base):
    info_hash: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    title: Mapped[str] = mapped_column(String, index=True, nullable=False)

    description: Mapped[str | None] = mapped_column(String, nullable=True)

    size: Mapped[int] = mapped_column(BigInteger, default=0)

    file_path: Mapped[str] = mapped_column(String, nullable=False)

    uploader_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))

    uploader = relationship("User", backref="torrents")