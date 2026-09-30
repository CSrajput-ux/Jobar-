import uuid
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from app.schemas.job import JobResponse
from app.services.connectors.greenhouse import greenhouse_connector
from app.services.connectors.lever import lever_connector
from app.services.connectors.remotive import remotive_connector
from app.services.ai_service import ai_service
from app.routers.profile import _mock_profile

router = APIRouter(prefix="/jobs", tags=["Job Discovery"])

_jobs_cache: List[dict] = [
    {
        "id": "e0000000-0000-0000-0000-000000000001",
        "companyName": "Linear",
        "title": "Staff Infrastructure & Systems Engineer",
        "location": "Remote (Worldwide)",
        "workMode": "remote",
        "descriptionText": "Scale distributed sync protocols, real-time WebSocket state coordination, and backend microservices at Linear.",
        "requirementsText": "8+ years backend systems experience. Deep mastery of TypeScript/Node, distributed state synchronization, PostgreSQL, Redis.",
        "salaryRange": "$180,000 - $220,000 + Equity",
        "source": "lever_api",
        "externalUrl": "https://jobs.lever.co/linear/staff-infrastructure-systems",
        "dedupHash": "hash_linear_staff_infra_2026",
        "atsType": "lever",
        "postedAt": "2026-09-26T14:30:00Z",
        "createdAt": "2026-09-26T14:30:00Z",
        "matchScore": 95
    },
    {
        "id": "e0000000-0000-0000-0000-000000000002",
        "companyName": "Vercel",
        "title": "Senior Full-Stack Engineer, AI Platforms",
        "location": "Remote (United States)",
        "workMode": "remote",
        "descriptionText": "Build developer tools and frontend infrastructure for next-generation generative AI web applications using Next.js App Router.",
        "requirementsText": "5+ years with React, Next.js, TypeScript, modern CSS. Experience integrating LLM APIs and streaming responses.",
        "salaryRange": "$170,000 - $210,000 + Equity",
        "source": "greenhouse_api",
        "externalUrl": "https://boards.greenhouse.io/vercel/jobs/5918239002",
        "dedupHash": "hash_vercel_fullstack_ai_2026",
        "atsType": "greenhouse",
        "postedAt": "2026-09-27T10:15:00Z",
        "createdAt": "2026-09-27T10:15:00Z",
        "matchScore": 96
    },
    {
        "id": "e0000000-0000-0000-0000-000000000003",
        "companyName": "Supabase",
        "title": "Backend Engineer, Postgres & Vector Engine",
        "location": "Remote",
        "workMode": "remote",
        "descriptionText": "Help scale Supabase pgvector and real-time database replication services for millions of developers worldwide.",
        "requirementsText": "Deep expertise in PostgreSQL internals, pgvector, distributed storage, Python or Go, and multi-tenant security.",
        "salaryRange": "$165,000 - $205,000 + Equity",
        "source": "greenhouse_api",
        "externalUrl": "https://boards.greenhouse.io/supabase/jobs/4829103002",
        "dedupHash": "hash_supabase_postgres_vector_2026",
        "atsType": "greenhouse",
        "postedAt": "2026-09-28T08:00:00Z",
        "createdAt": "2026-09-28T08:00:00Z",
        "matchScore": 93
    }
]

@router.get("", response_model=List[JobResponse])
async def list_jobs(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    workMode: Optional[str] = Query(None),
    minScore: Optional[int] = Query(None),
    atsType: Optional[str] = Query(None)
):
    results = _jobs_cache
    if query:
        q = query.lower()
        results = [j for j in results if q in j["title"].lower() or q in j["companyName"].lower() or q in j["descriptionText"].lower()]
    if location:
        results = [j for j in results if location.lower() in j["location"].lower()]
    if workMode:
        results = [j for j in results if workMode.lower() == j["workMode"].lower()]
    if atsType:
        results = [j for j in results if j.get("atsType") == atsType]
    if minScore:
        results = [j for j in results if j.get("matchScore", 0) >= minScore]
    return results

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    for j in _jobs_cache:
        if j["id"] == job_id:
            return j
    raise HTTPException(status_code=404, detail="Job not found")

@router.post("/sync")
async def sync_jobs():
    """
    Triggers discovery across Greenhouse, Lever, and Remotive feeds,
    deduplicating and computing semantic fit scores.
    """
    fetched_jobs = []
    
    # 1. Fetch from Greenhouse (e.g. Vercel, Supabase)
    vercel_jobs = await greenhouse_connector.fetch_jobs("vercel")
    supabase_jobs = await greenhouse_connector.fetch_jobs("supabase")
    
    # 2. Fetch from Lever (e.g. Linear)
    linear_jobs = await lever_connector.fetch_jobs("linear")
    
    # 3. Fetch from Remotive remote feed
    remote_jobs = await remotive_connector.fetch_jobs("software-dev")
    
    all_raw = vercel_jobs + supabase_jobs + linear_jobs + remote_jobs
    
    existing_hashes = {j["dedupHash"] for j in _jobs_cache}
    new_count = 0

    for raw in all_raw:
        if raw["dedupHash"] not in existing_hashes:
            job_obj = dict(raw)
            job_obj["id"] = str(uuid.uuid4())
            job_obj["createdAt"] = "2026-09-30T12:00:00Z"
            # Quick score
            match_eval = await ai_service.evaluate_job_match(_mock_profile, job_obj)
            job_obj["matchScore"] = match_eval.get("score", 78)
            _jobs_cache.insert(0, job_obj)
            existing_hashes.add(raw["dedupHash"])
            new_count += 1

    return {
        "status": "success",
        "syncedCount": len(all_raw),
        "newJobsIngested": new_count,
        "totalJobsInCatalog": len(_jobs_cache)
    }
