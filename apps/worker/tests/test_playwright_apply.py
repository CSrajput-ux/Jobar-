import pytest
from tasks.playwright_apply import apply_runner

@pytest.mark.asyncio
async def test_playwright_apply_flow():
    candidate_info = {
        "fullName": "Alex Chen",
        "email": "alex.chen.dev@gmail.com",
        "phone": "+1 (555) 019-2831",
        "linkedinUrl": "https://linkedin.com/in/alexchen-dev"
    }

    result = await apply_runner.apply_to_job(
        application_id="test_app_123",
        job_url="https://boards.greenhouse.io/vercel/jobs/5918239002",
        candidate_info=candidate_info
    )

    assert result["status"] in ["APPLIED", "NEEDS_ATTENTION"]
    assert "screenshotUrl" in result
    if result["status"] == "NEEDS_ATTENTION":
        # If CAPTCHA was encountered, it must correctly request manual action without breaking
        assert "reason" in result
