from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password


class AuthService:
    @staticmethod
    async def register_new_user(db: AsyncSession, user_in: UserCreate) -> User:
        # Проверяем, не занят ли email
        query = select(User).where(User.email == user_in.email)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Проверяем, не занят ли username
        query = select(User).where(User.username == user_in.username)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Создаем пользователя
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            is_superuser=False,
        )

        # Сохраняем в БД
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return db_user

    @staticmethod
    async def authenticate_user(
            db: AsyncSession,
            email: str,
            password: str
    ) -> User | None:
        """Ищет юзера по email и проверяет пароль"""
        # Ищем пользователя
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        # Если пользователя нет
        if not user:
            return None

        # Если пароль не правильный
        if not verify_password(password, user.hashed_password):
            return None

        return user