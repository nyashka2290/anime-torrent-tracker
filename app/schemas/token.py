from pydantic import BaseModel


class Token(BaseModel):
    """Ответ с токеном доступа"""
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """Содержимое JWT токена"""
    sub: int | None = None