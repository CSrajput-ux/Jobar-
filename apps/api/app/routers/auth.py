from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthService, LoginRequest, RegisterRequest, UserRecord
from app.db.database import get_db
from app.db.session import UserSessionRepository
from app.db.user import UserRepository
from app.schemas.auth import AuthResponse, RegisterResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        store=UserSessionRepository(session),
        repository=UserRepository(session),
    )


async def get_current_user(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> UserRecord:
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    user = await service.get_current_user(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    return user


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    existing = await service.get_user_by_email(str(payload.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
    user = await service.register(
        email=str(payload.email),
        password=payload.password,
        full_name=payload.full_name,
    )
    return RegisterResponse(user=user.model_dump(mode="json"))


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    session = await service.login(
        email=str(payload.email),
        password=payload.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    return AuthResponse(**session)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> None:
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if token:
        await service.logout(token)
