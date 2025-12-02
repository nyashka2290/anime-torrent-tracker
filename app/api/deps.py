from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/access-token")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сессии бд для Depends()"""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> User:
    """
    Проверяет JWT токен и возвращает текущего пользователя

    Args:
        db: Сессия базы данных
        token: JWT токен из заголовка Authorization

    Returns:
        Авторизованный пользователь

    Raises:
        HTTPException: 401 если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenPayload(sub=int(user_id_str))
    except JWTError:
        raise credentials_exception

    if token_data.sub is None:
        raise credentials_exception

    query = select(User).where(User.id == token_data.sub)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user