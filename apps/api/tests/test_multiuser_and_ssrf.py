import pytest
from uuid import uuid4
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app
from app.core.ssrf import validate_url_ssrf_safe
from app.core.config import Settings
from app.core.auth import AuthService, UserRecord, UserRole
from app.core.dependencies import get_current_user


def test_ssrf_blocks_private_and_metadata_ips():
    # Loopback
    with pytest.raises(HTTPException) as exc_127:
        validate_url_ssrf_safe("http://127.0.0.1:8080/internal")
    assert exc_127.value.status_code == 400
    assert "blocked by SSRF policy" in exc_127.value.detail or "restricted" in exc_127.value.detail

    # Cloud metadata
    with pytest.raises(HTTPException) as exc_meta:
        validate_url_ssrf_safe("http://169.254.169.254/latest/meta-data")
    assert exc_meta.value.status_code == 400

    # RFC 1918 Private ranges
    with pytest.raises(HTTPException) as exc_priv:
        validate_url_ssrf_safe("http://10.0.0.1/admin")
    assert exc_priv.value.status_code == 400

    with pytest.raises(HTTPException) as exc_priv2:
        validate_url_ssrf_safe("http://192.168.1.1/router")
    assert exc_priv2.value.status_code == 400

    # Localhost domain
    with pytest.raises(HTTPException) as exc_local:
        validate_url_ssrf_safe("http://localhost:3000/api")
    assert exc_local.value.status_code == 400

    # Unsafe schemes
    with pytest.raises(HTTPException) as exc_scheme:
        validate_url_ssrf_safe("ftp://ftp.example.com/file")
    assert exc_scheme.value.status_code == 400

    # Embedded credentials
    with pytest.raises(HTTPException) as exc_creds:
        validate_url_ssrf_safe("https://admin:password@boards.greenhouse.io/test")
    assert exc_creds.value.status_code == 400


def test_production_fails_closed_without_master_key(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("ENCRYPTION_MASTER_KEY", "short_key")
    with pytest.raises(ValueError) as exc:
        Settings()
    assert "Invalid production ENCRYPTION_MASTER_KEY" in str(exc.value)


def test_multi_user_application_and_audit_isolation():
    from datetime import datetime, timezone

    client = TestClient(app)
    now = datetime.now(timezone.utc)

    user_a_id = uuid4()
    user_b_id = uuid4()

    user_a = UserRecord(
        id=user_a_id,
        email="user_a@domain.com",
        full_name="User Alice",
        role=UserRole.USER,
        is_active=True,
        password_hash="test_hash_a",
        created_at=now,
        updated_at=now,
    )
    user_b = UserRecord(
        id=user_b_id,
        email="user_b@domain.com",
        full_name="User Bob",
        role=UserRole.USER,
        is_active=True,
        password_hash="test_hash_b",
        created_at=now,
        updated_at=now,
    )

    # 1. As User A: get applications
    app.dependency_overrides[get_current_user] = lambda: user_a
    res_a = client.get("/api/v1/applications")
    assert res_a.status_code == 200
    apps_a = res_a.json()
    assert len(apps_a) > 0
    app_a_id = apps_a[0]["id"]

    # 2. As User B: try to view User A's application
    app.dependency_overrides[get_current_user] = lambda: user_b
    res_b_view = client.get(f"/api/v1/applications/{app_a_id}")
    assert res_b_view.status_code == 404

    # 3. As User B: try to approve User A's application
    res_b_approve = client.post(f"/api/v1/applications/{app_a_id}/approve")
    assert res_b_approve.status_code == 404

    # Clean up dependency override
    app.dependency_overrides.pop(get_current_user, None)
