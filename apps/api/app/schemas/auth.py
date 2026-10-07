from datetime import datetime

from pydantic import BaseModel

from app.core.auth import LoginRequest, RegisterRequest


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: dict


class RegisterResponse(BaseModel):
    user: dict
