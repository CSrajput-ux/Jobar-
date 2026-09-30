from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any, Optional
from app.schemas.profile import StructuredProfileSchema, PreferencesSchema, CommonQASchema
from app.services.ai_service import ai_service

router = APIRouter(prefix="/profile", tags=["Profile & Onboarding"])

# In-memory mock storage for development & testing when DB is booting
_mock_profile: Dict[str, Any] = {
    "headline": "Staff Full-Stack & Distributed Systems Engineer",
    "summary": "Senior engineer with 8+ years building high-throughput cloud architectures, Python/FastAPI microservices, Next.js web applications, and resilient queue-driven automation.",
    "phone": "+1 (555) 019-2831",
    "location": "San Francisco, CA (Open to Remote)",
    "linkedinUrl": "https://linkedin.com/in/alexchen-dev",
    "githubUrl": "https://github.com/alexchen",
    "skills": {
        "technical": ["Python", "TypeScript", "Go", "PostgreSQL", "Redis", "Distributed Systems", "Kafka"],
        "frameworks": ["FastAPI", "Next.js", "React", "Node.js", "Celery", "Tailwind CSS"],
        "tools": ["Docker", "Kubernetes", "AWS", "Playwright", "Git", "Terraform", "CI/CD"],
        "languages": ["English (Native)", "Mandarin (Conversational)"]
    },
    "experience": [
        {
            "id": "exp-1",
            "company": "Veloce Cloud Systems",
            "title": "Staff Software Engineer",
            "startDate": "2021-03",
            "endDate": None,
            "isCurrent": True,
            "location": "Remote",
            "highlights": [
                "Architected event-driven microservices processing 45M daily events with 99.99% availability using FastAPI, Celery, and Redis.",
                "Designed high-performance vector search engine using pgvector, reducing semantic lookup latency from 450ms to 42ms.",
                "Mentored 6 engineers and spearheaded zero-downtime database schema migration workflows."
            ],
            "skillsUsed": ["Python", "FastAPI", "PostgreSQL", "pgvector", "Redis", "Docker"]
        },
        {
            "id": "exp-2",
            "company": "Aura AI Labs",
            "title": "Senior Full-Stack Engineer",
            "startDate": "2018-06",
            "endDate": "2021-02",
            "isCurrent": False,
            "location": "San Francisco, CA",
            "highlights": [
                "Built real-time Next.js analytics platform with TanStack Query and WebSockets serving 120,000 MAU.",
                "Implemented resilient browser automation agents with Playwright to extract structured insights from 200+ partner portals.",
                "Optimized frontend bundle size by 44% and established enterprise design system with Tailwind CSS."
            ],
            "skillsUsed": ["Next.js", "TypeScript", "React", "Playwright", "Tailwind CSS"]
        }
    ],
    "education": [
        {
            "id": "edu-1",
            "institution": "University of California, Berkeley",
            "degree": "B.S. in Electrical Engineering & Computer Science",
            "fieldOfStudy": "Computer Science",
            "startDate": "2014-08",
            "endDate": "2018-05"
        }
    ],
    "projects": [
        {
            "id": "proj-1",
            "name": "HyperScale Queue Gateway",
            "description": "Open-source asynchronous task dispatcher with distributed deduplication and backpressure telemetry.",
            "technologies": ["Python", "Redis", "FastAPI"]
        }
    ]
}

_mock_preferences: Dict[str, Any] = {
    "targetRoles": ["Staff Software Engineer", "Senior Full Stack Engineer", "Principal Backend Engineer"],
    "seniorityLevels": ["Senior", "Staff", "Principal"],
    "locations": ["Remote", "San Francisco, CA", "New York, NY"],
    "workModes": ["remote", "hybrid"],
    "minSalaryUsd": 175000,
    "visaSponsorshipRequired": False,
    "blacklistedCompanies": ["Meta", "CryptoCorp"],
    "targetIndustries": ["Developer Tools", "AI Infrastructure", "Enterprise Cloud"],
    "applyMode": "APPROVAL_QUEUE",
    "dailyApplyCap": 15,
    "minMatchScore": 75
}

_mock_common_qa: Dict[str, Any] = {
    "noticePeriodDays": 14,
    "workAuthStatus": "Authorized to work in US without sponsorship",
    "requiresSponsorship": False,
    "expectedSalaryUsd": 185000,
    "whyCompanyDefault": "Inspired by the high engineering bar, developer-first tooling, and scalable system architecture.",
    "customAnswers": {
        "preferred_cloud": "AWS & GCP",
        "open_source_contributions": "Active contributor to open-source Python and TypeScript ecosystems."
    }
}

@router.get("", response_model=StructuredProfileSchema)
async def get_profile():
    return _mock_profile

@router.post("/upload-cv", response_model=StructuredProfileSchema)
async def upload_cv(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None)
):
    text_content = raw_text or ""
    if file:
        content_bytes = await file.read()
        try:
            text_content = content_bytes.decode('utf-8', errors='ignore')
        except Exception:
            text_content = "Alex Chen - Staff Software Engineer with Python, TypeScript, FastAPI, Next.js experience."
    
    if not text_content.strip():
        text_content = "Alex Chen - Senior Full-Stack Engineer, expert in Python, Next.js, FastAPI, Docker, and PostgreSQL."

    parsed = await ai_service.parse_cv_text(text_content)
    global _mock_profile
    _mock_profile = parsed
    return parsed

@router.put("", response_model=StructuredProfileSchema)
async def update_profile(profile: StructuredProfileSchema):
    global _mock_profile
    _mock_profile = profile.model_dump()
    return _mock_profile

@router.get("/preferences", response_model=PreferencesSchema)
async def get_preferences():
    return _mock_preferences

@router.put("/preferences", response_model=PreferencesSchema)
async def update_preferences(prefs: PreferencesSchema):
    global _mock_preferences
    _mock_preferences = prefs.model_dump()
    return _mock_preferences

@router.get("/common-qa", response_model=CommonQASchema)
async def get_common_qa():
    return _mock_common_qa

@router.put("/common-qa", response_model=CommonQASchema)
async def update_common_qa(qa: CommonQASchema):
    global _mock_common_qa
    _mock_common_qa = qa.model_dump()
    return _mock_common_qa
