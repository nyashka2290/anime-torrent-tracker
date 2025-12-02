from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy import Integer


class Base(DeclarativeBase):
    """Базовая модель с автоматическим id и именем таблицы"""
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    @declared_attr.directive
    def __tablename__(self) -> str:
        """Генерирует имя таблицы из имени класса в нижнем регистре"""
        return self.__name__.lower()