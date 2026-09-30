import pytest
from app.services.ai_service import ai_service

@pytest.mark.asyncio
async def test_zero_fabrication_resume_tailoring():
    profile = {
        "headline": "Staff Software Engineer",
        "skills": {
            "technical": ["Python", "PostgreSQL", "FastAPI", "Redis"],
            "frameworks": ["Next.js", "React"],
            "tools": ["Docker"]
        },
        "experience": [
            {
                "id": "exp-1",
                "company": "Veloce Cloud Systems",
                "title": "Staff Engineer",
                "startDate": "2021-03",
                "highlights": [
                    "Architected event-driven microservices processing 45M daily events with 99.99% availability using FastAPI."
                ]
            }
        ]
    }
    
    job = {
        "title": "Senior Python Backend Engineer",
        "companyName": "Vercel",
        "descriptionText": "Looking for deep Python and FastAPI experience."
    }

    result = await ai_service.generate_tailored_resume(profile, job)
    
    assert "bulletDiffs" in result
    assert len(result["bulletDiffs"]) > 0
    # Verify no new company names were invented
    for exp in result["tailoredExperience"]:
        assert exp["company"] == "Veloce Cloud Systems"
    
    # Check cover letter was generated
    assert "Vercel" in result["matchingCoverLetter"]
    assert "45M daily events" in result["matchingCoverLetter"]

@pytest.mark.asyncio
async def test_inbound_email_intent_classification():
    # Test Interview Invite
    invite = await ai_service.classify_inbound_email(
        subject="Invitation to Interview: Backend Engineer @ Supabase",
        body="We loved your background and would like to schedule an introductory call.",
        sender="careers@supabase.com"
    )
    assert invite["classification"] == "INTERVIEW_INVITE"
    assert invite["actionRequired"] is True
    assert invite["proposedReplyText"] is not None

    # Test Rejection
    rejection = await ai_service.classify_inbound_email(
        subject="Status update on your application",
        body="Unfortunately, we have decided to move forward with other candidates.",
        sender="talent@stripe.com"
    )
    assert rejection["classification"] == "REJECTION"
    assert rejection["actionRequired"] is False
