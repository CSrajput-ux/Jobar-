import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_list_jobs_endpoint():
    res = client.get("/api/v1/jobs")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 3

def test_profile_endpoint():
    res = client.get("/api/v1/profile")
    assert res.status_code == 200
    data = res.json()
    assert "headline" in data
    assert "experience" in data

def test_application_approval_flow():
    # 1. Get applications
    res = client.get("/api/v1/applications")
    assert res.status_code == 200
    apps = res.json()
    assert len(apps) > 0
    queued = next((a for a in apps if a["status"] == "QUEUED_FOR_APPROVAL"), None)
    
    if queued:
        # 2. Approve application
        app_id = queued["id"]
        approve_res = client.post(f"/api/v1/applications/{app_id}/approve")
        assert approve_res.status_code == 200
        approved_data = approve_res.json()
        assert approved_data["status"] == "APPLIED"
        assert approved_data["proofScreenshotUrl"] is not None

def test_emergency_kill_switch():
    # Engage kill switch
    res = client.post("/api/v1/audit/kill-switch", json={"active": True})
    assert res.status_code == 200
    assert res.json()["killSwitchActive"] is True

    # Check status
    status_res = client.get("/api/v1/audit/status")
    assert status_res.status_code == 200
    assert status_res.json()["killSwitchActive"] is True

    # Disengage
    res_off = client.post("/api/v1/audit/kill-switch", json={"active": False})
    assert res_off.status_code == 200
    assert res_off.json()["killSwitchActive"] is False
