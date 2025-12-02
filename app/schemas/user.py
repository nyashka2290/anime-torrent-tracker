from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    """Базовые поля пользователя"""
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """Схема для регистрации пользователя"""
    password: str

class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    model_config = ConfigDict(from_attributes=True)