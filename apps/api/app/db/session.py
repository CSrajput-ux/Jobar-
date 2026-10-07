from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserSession


class UserSessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> dict:
        session = UserSession(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session.add(session)
        await self.session.flush()
        return {
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "user_agent": user_agent,
            "ip_address": ip_address,
        }

    async def get(self, token_hash: str) -> dict | None:
        statement = select(UserSession).where(UserSession.token_hash == token_hash)
        result = await self.session.execute(statement)
        session = result.scalar_one_or_none()
        if session is None:
            return None
        return {
            "user_id": session.user_id,
            "expires_at": session.expires_at,
            "user_agent": session.user_agent,
            "ip_address": session.ip_address,
        }

    async def revoke(self, token_hash: str) -> None:
        statement = delete(UserSession).where(UserSession.token_hash == token_hash)
        await self.session.execute(statement)

    async def purge_expired(self, now: datetime | None = None) -> int:
        now = now or datetime.now(timezone.utc)
        statement = delete(UserSession).where(UserSession.expires_at <= now)
        result = await self.session.execute(statement)
        return result.rowcount or 0
