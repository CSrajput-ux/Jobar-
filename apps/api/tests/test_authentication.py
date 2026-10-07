import pytest
from fastapi import HTTPException

from app.core.auth import AuthService, UserRecord, UserRole


class FakeUserRepository:
    def __init__(self):
        self.users = {}

    async def create(self, user):
        self.users[user.email] = user
        return user

    async def get_by_email(self, email):
        return self.users.get(email)

    async def get_by_id(self, user_id):
        return next((user for user in self.users.values() if user.id == user_id), None)

    async def update(self, user):
        self.users[user.email] = user
        return user


class FakeSessionStore:
    def __init__(self):
        self.sessions = {}

    async def create(self, user_id, token_hash, expires_at, user_agent, ip_address):
        self.sessions[token_hash] = {
            "user_id": user_id,
            "expires_at": expires_at,
            "user_agent": user_agent,
            "ip_address": ip_address,
        }
        return self.sessions[token_hash]

    async def get(self, token_hash):
        return self.sessions.get(token_hash)

    async def revoke(self, token_hash):
        self.sessions.pop(token_hash, None)


@pytest.mark.asyncio
async def test_register_login_and_logout_flow():
    repository = FakeUserRepository()
    service = AuthService(store=FakeSessionStore(), repository=repository)
    await service.register(
        email="candidate@example.com",
        password="StrongPassword!2026",
        full_name="Candidate Example",
    )

    session = await service.login(
        email="candidate@example.com",
        password="StrongPassword!2026",
        user_agent="test-agent",
        ip_address="127.0.0.1",
    )

    assert session["access_token"]
    assert session["user"]["role"] == UserRole.USER
    assert await service.logout(session["access_token"])
    assert await service.get_current_user(session["access_token"]) is None


@pytest.mark.asyncio
async def test_wrong_password_and_inactive_account_are_rejected():
    repository = FakeUserRepository()
    service = AuthService(store=FakeSessionStore(), repository=repository)
    await service.register(
        email="candidate@example.com",
        password="StrongPassword!2026",
        full_name="Candidate Example",
    )

    with pytest.raises(HTTPException) as exc:
        await service.login(
            email="candidate@example.com",
            password="wrong-password",
            user_agent="test-agent",
            ip_address="127.0.0.1",
        )
    assert exc.value.status_code == 401

    user = await service.get_user_by_email("candidate@example.com")
    user.is_active = False
    with pytest.raises(HTTPException) as exc:
        await service.login(
            email="candidate@example.com",
            password="StrongPassword!2026",
            user_agent="test-agent",
            ip_address="127.0.0.1",
        )
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_password_is_never_stored_in_plaintext():
    repository = FakeUserRepository()
    service = AuthService(store=FakeSessionStore(), repository=repository)
    user = await service.register(
        email="candidate@example.com",
        password="StrongPassword!2026",
        full_name="Candidate Example",
    )

    assert user.password_hash != "StrongPassword!2026"
    assert user.password_hash.startswith("$argon2")
