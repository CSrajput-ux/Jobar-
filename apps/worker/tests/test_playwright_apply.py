import pytest
from tasks.playwright_apply import apply_runner
from tasks.discovery_tasks import sync_all_job_feeds
from tasks.email_tasks import poll_inbox_updates, send_outreach_email

@pytest.mark.asyncio
async def test_playwright_apply_flow():
    candidate_info = {
        "fullName": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+1 (555) 019-2831",
        "linkedinUrl": "https://linkedin.com/in/janedoe"
    }

    result = await apply_runner.apply_to_job(
        application_id="test_app_123",
        job_url="https://boards.greenhouse.io/vercel/jobs/5918239002",
        candidate_info=candidate_info
    )

    assert result["status"] == "NEEDS_ATTENTION"
    assert "screenshotUrl" in result
    if result["status"] == "NEEDS_ATTENTION":
        assert "reason" in result


def test_discovery_task_reports_sources():
    result = sync_all_job_feeds()
    assert result["status"] == "COMPLETED"
    assert "sources" in result
    assert "timestamp" in result


def test_email_task_guards_unconfigured_provider():
    # Unconfigured provider fails safely with NOT_CONFIGURED
    res_unauth = send_outreach_email(
        email_id="outreach_01",
        recipient="recruiter@target.com",
        subject="Intro",
        body="Hello",
        provider_connected=False,
    )
    assert res_unauth["status"] == "NOT_CONFIGURED"
    assert "Google Workspace OAuth connection is not active" in res_unauth["reason"]

    # Connected provider returns SENT with timestamp
    res_auth = send_outreach_email(
        email_id="outreach_02",
        recipient="recruiter@target.com",
        subject="Intro",
        body="Hello",
        provider_connected=True,
    )
    assert res_auth["status"] == "SENT"
    assert "dispatchedAt" in res_auth
