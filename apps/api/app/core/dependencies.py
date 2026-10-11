from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.auth import AuthService, UserRecord, UserRole
from app.db.database import get_db
from app.db.session import UserSessionRepository
from app.db.user import UserRepository
from app.db.repositories import (
    ProfileRepository,
    JobRepository,
    MatchRepository,
    ApplicationRepository,
    OutreachRepository,
    InboxRepository,
    CalendarRepository,
    AuditRepository,
)


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        store=UserSessionRepository(session),
        repository=UserRepository(session),
    )


async def get_current_user(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> UserRecord:
    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
    elif "session_token" in request.cookies:
        token = request.cookies.get("session_token", "").strip()

    if not token:
        # In production mode, always enforce authentication strictly
        if settings.ENVIRONMENT == "production":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please provide a valid Bearer token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # In development / testing mode, allow test user context for unauthenticated test harness
        dev_user_id = UUID("a0000000-0000-0000-0000-000000000001")
        if service.repository:
            existing = await service.repository.get_by_id(dev_user_id)
            if existing:
                return existing

        now = datetime.now(timezone.utc)
        return UserRecord(
            id=dev_user_id,
            email="candidate@jobpilot.dev",
            full_name="Alex Chen",
            role=UserRole.USER,
            is_active=True,
            password_hash="argon2id$development_stub",
            created_at=now,
            updated_at=now,
        )

    user = await service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or is invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    return user


async def require_admin(
    user: UserRecord = Depends(get_current_user),
) -> UserRecord:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required.",
        )
    return user


def get_profile_repo(session: AsyncSession = Depends(get_db)) -> ProfileRepository:
    return ProfileRepository(session)


def get_job_repo(session: AsyncSession = Depends(get_db)) -> JobRepository:
    return JobRepository(session)


def get_match_repo(session: AsyncSession = Depends(get_db)) -> MatchRepository:
    return MatchRepository(session)


def get_app_repo(session: AsyncSession = Depends(get_db)) -> ApplicationRepository:
    return ApplicationRepository(session)


def get_outreach_repo(session: AsyncSession = Depends(get_db)) -> OutreachRepository:
    return OutreachRepository(session)


def get_inbox_repo(session: AsyncSession = Depends(get_db)) -> InboxRepository:
    return InboxRepository(session)


def get_calendar_repo(session: AsyncSession = Depends(get_db)) -> CalendarRepository:
    return CalendarRepository(session)


def get_audit_repo(session: AsyncSession = Depends(get_db)) -> AuditRepository:
    return AuditRepository(session)
