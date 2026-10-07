from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import UserRecord
from app.db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserRecord) -> UserRecord:
        record = User(
            id=user.id,
            email=str(user.email),
            full_name=user.full_name,
            password_hash=user.password_hash,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return UserRecord(
            id=record.id,
            email=record.email,
            full_name=record.full_name,
            role=record.role,
            is_active=record.is_active,
            password_hash=record.password_hash,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    async def get_by_email(self, email: str) -> UserRecord | None:
        statement = select(User).where(User.email == email.lower())
        result = await self.session.execute(statement)
        record = result.scalar_one_or_none()
        return self._to_record(record)

    async def get_by_id(self, user_id: UUID) -> UserRecord | None:
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        record = result.scalar_one_or_none()
        return self._to_record(record)

    @staticmethod
    def _to_record(record: User | None) -> UserRecord | None:
        if record is None:
            return None
        return UserRecord(
            id=record.id,
            email=record.email,
            full_name=record.full_name,
            role=record.role,
            is_active=record.is_active,
            password_hash=record.password_hash,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
