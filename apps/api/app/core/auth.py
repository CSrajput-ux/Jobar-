from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Protocol
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from fastapi import HTTPException, Request
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserRecord(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    password_hash: str
    created_at: datetime
    updated_at: datetime


class UserRepository(Protocol):
    async def create(self, user: UserRecord) -> UserRecord: ...

    async def get_by_email(self, email: str) -> UserRecord | None: ...

    async def get_by_id(self, user_id: UUID) -> UserRecord | None: ...

    async def update(self, user: UserRecord) -> UserRecord: ...


class SessionStore(Protocol):
    async def create(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> dict: ...

    async def get(self, token_hash: str) -> dict | None: ...

    async def revoke(self, token_hash: str) -> None: ...


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not any(character.isupper() for character in value):
            raise ValueError("password must include an uppercase character")
        if not any(character.isdigit() for character in value):
            raise ValueError("password must include a number")
        if not any(character in "!@#$%^&*()_+-=[]{}|;:,.<>?" for character in value):
            raise ValueError("password must include a special character")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AuthService:
    def __init__(
        self,
        store: SessionStore,
        repository: UserRepository | None = None,
        password_hasher=None,
    ):
        self.store = store
        self.repository = repository
        self.password_hasher = password_hasher or PasswordHasher(
            time_cost=3,
            memory_cost=64 * 1024,
            parallelism=4,
            hash_len=32,
            salt_len=16,
        )
        self.session_ttl = timedelta(days=30)

    async def register(self, email: str, password: str, full_name: str) -> UserRecord:
        if self.repository is None:
            raise RuntimeError("User repository must be configured")
        now = datetime.now(timezone.utc)
        user = UserRecord(
            id=uuid4(),
            email=email,
            full_name=full_name.strip(),
            password_hash=self.password_hasher.hash(password),
            created_at=now,
            updated_at=now,
        )
        return await self.repository.create(user)

    async def login(
        self,
        email: str,
        password: str,
        user_agent: str | None,
        ip_address: str | None,
    ) -> dict:
        user = await self.get_user_by_email(email)
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        try:
            password_valid = self.password_hasher.verify(
                user.password_hash,
                password,
            )
        except Exception:
            password_valid = False
        if not password_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + self.session_ttl
        await self.store.create(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_at": expires_at,
            "user": user.model_dump(mode="json"),
        }

    async def get_user_by_email(self, email: str) -> UserRecord | None:
        if self.repository is None:
            raise RuntimeError("User repository must be configured")
        return await self.repository.get_by_email(email)

    async def get_current_user(self, token: str) -> UserRecord | None:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        session = await self.store.get(token_hash)
        if session is None or session["expires_at"] <= datetime.now(timezone.utc):
            return None
        if self.repository is None:
            raise RuntimeError("User repository must be configured")
        return await self.repository.get_by_id(session["user_id"])

    async def logout(self, token: str) -> bool:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        await self.store.revoke(token_hash)
        return True


def get_current_user(request: Request) -> UserRecord:
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    raise HTTPException(status_code=501, detail="User context is not configured")


def require_role(role: UserRole):
    def dependency(user: UserRecord = None):
        if user is None or user.role != role:
            raise HTTPException(status_code=403, detail="Authorization required")
        return user

    return dependency
