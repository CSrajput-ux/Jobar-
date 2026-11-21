import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_platforms_listing_and_defaults():
    res = client.get("/api/v1/platforms")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    wellfound = next((p for p in data if p["id"] == "wellfound"), None)
    assert wellfound is not None
    assert "autoApplyEnabled" in wellfound


def test_platforms_auto_apply_settings_crud():
    # Get settings
    get_res = client.get("/api/v1/platforms/auto-apply/settings")
    assert get_res.status_code == 200
    settings = get_res.json()
    assert "autoPilotActive" in settings
    assert "dailyApplyCap" in settings
    assert "minMatchScore" in settings

    # Update settings
    update_res = client.put(
        "/api/v1/platforms/auto-apply/settings",
        json={
            "autoPilotActive": False,
            "dailyApplyCap": 25,
            "minMatchScore": 90,
            "maxApplicationsPerHour": 6,
        },
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["status"] == "success"
    assert updated["config"]["dailyApplyCap"] == 25
    assert updated["config"]["minMatchScore"] == 90


def test_platforms_connect_and_auto_apply_run():
    # Connect platform
    connect_res = client.post(
        "/api/v1/platforms/connect",
        json={
            "platformId": "wellfound",
            "accountEmail": "test.user@example.com",
            "credentialsStored": True,
        },
    )
    assert connect_res.status_code == 200
    assert connect_res.json()["status"] == "success"

    # Trigger auto-apply
    run_res = client.post(
        "/api/v1/platforms/auto-apply/run",
        json={"platformId": "wellfound", "forceRun": True},
    )
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert "jobId" in run_data or "status" in run_data

    # Retrieve logs
    logs_res = client.get("/api/v1/platforms/auto-apply/logs")
    assert logs_res.status_code == 200
    assert isinstance(logs_res.json(), list)


def test_outreach_endpoints():
    contacts_res = client.get("/api/v1/outreach/contacts")
    assert contacts_res.status_code == 200
    assert isinstance(contacts_res.json(), list)

    emails_res = client.get("/api/v1/outreach/emails")
    assert emails_res.status_code == 200
    assert isinstance(emails_res.json(), list)


def test_inbox_endpoints():
    threads_res = client.get("/api/v1/inbox/threads")
    assert threads_res.status_code == 200
    assert isinstance(threads_res.json(), list)

    # Inbound email classification
    classify_res = client.post(
        "/api/v1/inbox/classify",
        json={
            "subject": "Invitation to Interview: Senior Backend Engineer",
            "body": "Hi Alex, We were very impressed with your profile and would love to schedule a 30-minute introductory call next week.",
            "sender": "recruiter@techcorp.io",
        },
    )
    assert classify_res.status_code == 200
    data = classify_res.json()
    assert "classification" in data or "confidence" in data or "proposed_reply" in data


def test_calendar_endpoints():
    events_res = client.get("/api/v1/calendar/events")
    assert events_res.status_code == 200
    assert isinstance(events_res.json(), list)

    slots_res = client.post("/api/v1/calendar/propose-slots")
    assert slots_res.status_code == 200
    slots_data = slots_res.json()
    assert "proposedSlots" in slots_data
    assert isinstance(slots_data["proposedSlots"], list)


def test_audit_logs_retrieval():
    res = client.get("/api/v1/audit/logs")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
