from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

class UserBase(BaseModel):
    """Базовые поля пользователя"""
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """Схема для регистрации пользователя"""
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Проверяет что пароль не короче 6 символов"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Проверяет что username не пустой и не слишком короткий"""
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v

class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    model_config = ConfigDict(from_attributes=True)