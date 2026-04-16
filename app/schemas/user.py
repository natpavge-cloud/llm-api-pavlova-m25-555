from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RegisterRequest(BaseModel):
    """Схема запроса регистрации."""

    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "user@example.com", "password": "securepassword123"}
        }
    )


class TokenResponse(BaseModel):
    """Схема ответа с JWT токеном."""

    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )
