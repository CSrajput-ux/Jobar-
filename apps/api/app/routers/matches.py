from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
from app.schemas.match import JobMatchResponse, TailoredResumeSchema
from app.services.ai_service import ai_service
from app.routers.profile import _mock_profile
from app.routers.jobs import _jobs_cache

router = APIRouter(prefix="/matches", tags=["AI Matching & Tailoring"])

_matches_cache: Dict[str, dict] = {
    "e0000000-0000-0000-0000-000000000002": {
        "id": "f0000000-0000-0000-0000-000000000001",
        "userId": "a0000000-0000-0000-0000-000000000001",
        "jobId": "e0000000-0000-0000-0000-000000000002",
        "score": 96,
        "reasoning": {
            "score": 96,
            "matchedSkills": ["Next.js", "TypeScript", "FastAPI", "React", "Tailwind CSS", "LLM APIs"],
            "missingSkills": [],
            "redFlags": [],
            "fitSummary": "Exceptional fit. Alex has 8+ years hands-on production Next.js and high-performance API experience directly matching Vercel AI platform priorities.",
            "seniorityAlignment": "ideal"
        },
        "createdAt": "2026-09-27T10:15:00Z"
    },
    "e0000000-0000-0000-0000-000000000003": {
        "id": "f0000000-0000-0000-0000-000000000002",
        "userId": "a0000000-0000-0000-0000-000000000001",
        "jobId": "e0000000-0000-0000-0000-000000000003",
        "score": 93,
        "reasoning": {
            "score": 93,
            "matchedSkills": ["PostgreSQL", "pgvector", "Python", "Distributed Systems", "Redis"],
            "missingSkills": ["Go Internals"],
            "redFlags": [],
            "fitSummary": "Outstanding backend alignment with direct pgvector production experience reducing query latency by 90%.",
            "seniorityAlignment": "ideal"
        },
        "createdAt": "2026-09-28T08:00:00Z"
    },
    "e0000000-0000-0000-0000-000000000001": {
        "id": "f0000000-0000-0000-0000-000000000003",
        "userId": "a0000000-0000-0000-0000-000000000001",
        "jobId": "e0000000-0000-0000-0000-000000000001",
        "score": 95,
        "reasoning": {
            "score": 95,
            "matchedSkills": ["Distributed Systems", "TypeScript", "Redis", "PostgreSQL", "Kafka"],
            "missingSkills": [],
            "redFlags": [],
            "fitSummary": "High alignment for Linear's distributed synchronization architecture. Proven experience with high-throughput event architectures.",
            "seniorityAlignment": "ideal"
        },
        "createdAt": "2026-09-26T14:30:00Z"
    }
}

@router.get("/{job_id}", response_model=JobMatchResponse)
async def get_match_for_job(job_id: str):
    if job_id in _matches_cache:
        return _matches_cache[job_id]
    
    # Compute on the fly if not cached
    job = next((j for j in _jobs_cache if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    reasoning = await ai_service.evaluate_job_match(_mock_profile, job)
    match_obj = {
        "id": f"match_{job_id[:8]}",
        "userId": "a0000000-0000-0000-0000-000000000001",
        "jobId": job_id,
        "score": reasoning["score"],
        "reasoning": reasoning,
        "createdAt": "2026-09-30T12:00:00Z"
    }
    _matches_cache[job_id] = match_obj
    return match_obj

@router.post("/tailor-resume/{job_id}", response_model=TailoredResumeSchema)
async def tailor_resume(job_id: str):
    job = next((j for j in _jobs_cache if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    tailored = await ai_service.generate_tailored_resume(_mock_profile, job)
    if job_id in _matches_cache:
        _matches_cache[job_id]["tailoredResume"] = tailored
    return tailored
