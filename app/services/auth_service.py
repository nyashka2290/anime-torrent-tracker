from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    """Сервис аутентификации и регистрации пользователей"""
    @staticmethod
    async def register_new_user(db: AsyncSession, user_in: UserCreate) -> User:
        """
        Регистрирует нового пользователя

        Args:
            db: Сессия базы данных
            user_in: Данные для создания пользователя

        Returns:
            Созданный пользователь

        Raises:
            HTTPException: Если email или username уже заняты
        """
        query = select(User).where(User.email == user_in.email)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        query = select(User).where(User.username == user_in.username)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            is_superuser=False,
        )

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
        """
        Аутентификация пользователя по email и паролю

        Args:
            db: Сессия базы данных
            email: Email пользователя
            password: Пароль в открытом виде

        Returns:
            Пользователь если аутентификация успешна, иначе None
        """
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user