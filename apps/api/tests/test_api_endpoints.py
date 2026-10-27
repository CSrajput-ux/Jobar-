import pytest
import uuid
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

def test_profile_endpoint():
    res = client.get("/api/v1/profile")
    assert res.status_code == 200
    data = res.json()
    assert "headline" in data
    assert "experience" in data

def test_application_approval_flow():
    job_res = client.post("/api/v1/jobs", json={
        "companyName": "Test Company",
        "title": "Platform Engineer",
        "externalUrl": f"https://jobs.example.test/{uuid.uuid4()}",
    })
    assert job_res.status_code == 201
    app_res = client.post("/api/v1/applications", json={
        "jobId": job_res.json()["id"],
        "status": "QUEUED_FOR_APPROVAL",
    })
    assert app_res.status_code == 201

    approve_res = client.post(f"/api/v1/applications/{app_res.json()['id']}/approve")
    assert approve_res.status_code == 200
    approved_data = approve_res.json()
    assert approved_data["status"] == "APPROVED"
    assert approved_data["approvedAt"] is not None
    assert approved_data["appliedAt"] is None
    assert approved_data["proofScreenshotUrl"] is None


def test_application_cannot_be_manually_marked_applied():
    apps = client.get("/api/v1/applications").json()
    approved = next((a for a in apps if a["status"] == "APPROVED"), None)
    if approved:
        res = client.patch(f"/api/v1/applications/{approved['id']}", json={"status": "APPLIED"})
        assert res.status_code == 409

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
