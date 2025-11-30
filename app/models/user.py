from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base_class import Base


class User(Base):
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)