from __future__ import annotations

from typing import Dict, Any, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.match import JobMatchResponse, TailoredResumeSchema
from app.services.ai_service import ai_service
from app.core.dependencies import (
    get_current_user,
    get_match_repo,
    get_job_repo,
    get_profile_repo,
)
from app.core.auth import UserRecord
from app.db.repositories import MatchRepository, JobRepository, ProfileRepository

router = APIRouter(prefix="/matches", tags=["AI Matching & Tailoring"])


@router.get("/{job_id}", response_model=JobMatchResponse)
async def get_match_for_job(
    job_id: str,
    current_user: UserRecord = Depends(get_current_user),
    match_repo: MatchRepository = Depends(get_match_repo),
    job_repo: JobRepository = Depends(get_job_repo),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    try:
        parsed_job_id = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid job ID format.")

    job = await job_repo.get_by_id(parsed_job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    # Check for existing match in database
    existing_match = await match_repo.get(current_user.id, parsed_job_id)
    if existing_match:
        return {
            "id": str(existing_match.id),
            "userId": str(existing_match.user_id),
            "jobId": str(existing_match.job_id),
            "score": existing_match.score,
            "reasoning": existing_match.reasoning,
            "createdAt": existing_match.created_at.isoformat() if existing_match.created_at else None,
        }

    # Retrieve candidate profile
    profile = await profile_repo.get_or_create(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_email=str(current_user.email),
    )
    profile_dict = {
        "headline": profile.headline,
        "summary": profile.summary,
        "skills": profile.skills or {},
        "experience": profile.experience or [],
    }

    job_dict = {
        "title": job.title,
        "companyName": job.company_name,
        "descriptionText": job.description_text,
        "requirementsText": job.requirements_text or "",
    }

    reasoning = await ai_service.evaluate_job_match(profile_dict, job_dict)
    score = reasoning.get("score", 75)

    saved = await match_repo.upsert(
        user_id=current_user.id,
        job_id=parsed_job_id,
        score=score,
        reasoning=reasoning,
    )
    return {
        "id": str(saved.id),
        "userId": str(saved.user_id),
        "jobId": str(saved.job_id),
        "score": saved.score,
        "reasoning": saved.reasoning,
        "createdAt": saved.created_at.isoformat() if saved.created_at else None,
    }


@router.post("/tailor-resume/{job_id}", response_model=TailoredResumeSchema)
async def tailor_resume(
    job_id: str,
    current_user: UserRecord = Depends(get_current_user),
    match_repo: MatchRepository = Depends(get_match_repo),
    job_repo: JobRepository = Depends(get_job_repo),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    try:
        parsed_job_id = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid job ID format.")

    job = await job_repo.get_by_id(parsed_job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    profile = await profile_repo.get_or_create(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_email=str(current_user.email),
    )
    profile_dict = {
        "headline": profile.headline,
        "summary": profile.summary,
        "skills": profile.skills or {},
        "experience": profile.experience or [],
    }

    job_dict = {
        "title": job.title,
        "companyName": job.company_name,
        "descriptionText": job.description_text,
        "requirementsText": job.requirements_text or "",
    }

    tailored = await ai_service.generate_tailored_resume(profile_dict, job_dict)
    await match_repo.upsert(
        user_id=current_user.id,
        job_id=parsed_job_id,
        score=85,
        reasoning={"summary": "Tailored for job"},
        tailored_resume_json=tailored,
    )
    return tailored
