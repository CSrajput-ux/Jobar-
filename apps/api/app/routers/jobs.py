from __future__ import annotations

import hashlib
import uuid
from urllib.parse import urlparse
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Query, HTTPException, Depends, status

from app.schemas.job import JobResponse
from app.services.connectors.greenhouse import greenhouse_connector
from app.services.connectors.lever import lever_connector
from app.services.connectors.remotive import remotive_connector
from app.core.dependencies import get_job_repo
from app.db.repositories import JobRepository
from app.db.models import Job

router = APIRouter(prefix="/jobs", tags=["Job Discovery"])


def _to_job_response(job: Job) -> Dict[str, Any]:
    return {
        "id": str(job.id),
        "companyName": job.company_name,
        "title": job.title,
        "location": job.location,
        "workMode": job.work_mode,
        "descriptionText": job.description_text,
        "requirementsText": job.requirements_text or "",
        "salaryRange": job.salary_range or "Competitive",
        "source": job.source,
        "externalUrl": job.external_url,
        "dedupHash": job.dedup_hash,
        "atsType": job.ats_type,
        "postedAt": job.posted_at.isoformat() if job.posted_at else None,
        "createdAt": job.created_at.isoformat() if job.created_at else None,
        "matchScore": 85,
    }


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    workMode: Optional[str] = Query(None),
    atsType: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    job_repo: JobRepository = Depends(get_job_repo),
):
    jobs = await job_repo.list_jobs(
        query=query,
        location=location,
        work_mode=workMode,
        ats_type=atsType,
        limit=limit,
        offset=offset,
    )

    return [_to_job_response(j) for j in jobs]


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_or_clip_job(
    payload: Dict[str, Any],
    job_repo: JobRepository = Depends(get_job_repo),
):
    """
    Ingests a job posting from the Chrome browser extension or manual submission.
    Deduplicates via stable hash of external URL or company + title.
    """
    company_name = payload.get("companyName") or payload.get("company_name")
    title = payload.get("title")
    external_url = payload.get("externalUrl") or payload.get("external_url")
    if not company_name or not title or not external_url:
        raise HTTPException(status_code=422, detail="companyName, title, and externalUrl are required.")
    parsed_url = urlparse(external_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise HTTPException(status_code=422, detail="externalUrl must be an absolute HTTP(S) URL.")
    
    dedup_hash = payload.get("dedupHash") or payload.get("dedup_hash")
    if not dedup_hash:
        raw_fingerprint = f"{company_name.lower().strip()}:{title.lower().strip()}:{external_url.strip()}"
        dedup_hash = hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()

    job_data = {
        "id": uuid.uuid4(),
        "company_name": company_name,
        "title": title,
        "location": payload.get("location", "Remote"),
        "work_mode": payload.get("workMode") or payload.get("work_mode", "remote"),
        "description_text": payload.get("descriptionText") or payload.get("description_text", title),
        "requirements_text": payload.get("requirementsText") or payload.get("requirements_text", ""),
        "salary_range": payload.get("salaryRange") or payload.get("salary_range"),
        "source": payload.get("source", "extension"),
        "external_url": external_url,
        "dedup_hash": dedup_hash,
        "ats_type": payload.get("atsType") or payload.get("ats_type"),
    }
    saved_job = await job_repo.upsert(job_data)
    return _to_job_response(saved_job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    job_repo: JobRepository = Depends(get_job_repo),
):
    try:
        parsed_id = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid job ID format.")

    job = await job_repo.get_by_id(parsed_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return _to_job_response(job)


@router.post("/sync")
async def sync_jobs(job_repo: JobRepository = Depends(get_job_repo)):
    """
    Executes live discovery across Greenhouse, Lever, and Remotive feeds,
    deduplicating and persisting to the database.
    """
    fetched_jobs = []
    
    # 1. Fetch from Greenhouse
    try:
        vercel_jobs = await greenhouse_connector.fetch_jobs("vercel")
        supabase_jobs = await greenhouse_connector.fetch_jobs("supabase")
        fetched_jobs.extend(vercel_jobs + supabase_jobs)
    except Exception as e:
        print(f"[JobsSync] Greenhouse connector error: {e}")

    # 2. Fetch from Lever
    try:
        linear_jobs = await lever_connector.fetch_jobs("linear")
        fetched_jobs.extend(linear_jobs)
    except Exception as e:
        print(f"[JobsSync] Lever connector error: {e}")

    # 3. Fetch from Remotive
    try:
        remote_jobs = await remotive_connector.fetch_jobs("software-dev")
        fetched_jobs.extend(remote_jobs)
    except Exception as e:
        print(f"[JobsSync] Remotive connector error: {e}")

    new_count = 0
    for raw in fetched_jobs:
        dedup_hash = raw.get("dedup_hash") or raw.get("dedupHash")
        if dedup_hash and not await job_repo.get_by_dedup_hash(dedup_hash):
            new_count += 1
        await job_repo.upsert(raw)

    all_current = await job_repo.list_jobs(limit=1000)
    return {
        "status": "success",
        "syncedCount": len(fetched_jobs),
        "newJobsIngested": new_count,
        "totalJobsInCatalog": len(all_current),
    }
