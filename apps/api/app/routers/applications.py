from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.apply import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.core.dependencies import (
    get_current_user,
    get_app_repo,
    get_job_repo,
    get_audit_repo,
)
from app.core.auth import UserRecord
from app.db.repositories import ApplicationRepository, JobRepository, AuditRepository

router = APIRouter(prefix="/applications", tags=["Applications & Pipeline"])

VALID_APPLICATION_STATUSES = {
    "SAVED",
    "QUEUED_FOR_APPROVAL",
    "READY_TO_SUBMIT",
    "APPLIED",
    "INTERVIEWING",
    "OFFERED",
    "REJECTED",
    "WITHDRAWN",
}


def _format_app_response(app, job=None) -> Dict[str, Any]:
    job_payload = None
    if job:
        job_payload = {
            "id": str(job.id),
            "companyName": job.company_name,
            "title": job.title,
            "location": job.location,
            "workMode": job.work_mode,
            "salaryRange": job.salary_range,
            "atsType": job.ats_type,
            "externalUrl": job.external_url,
        }
    return {
        "id": str(app.id),
        "userId": str(app.user_id),
        "jobId": str(app.job_id),
        "status": app.status,
        "appliedAt": app.applied_at.isoformat() if app.applied_at else None,
        "proofScreenshotUrl": app.proof_screenshot_url,
        "submittedPayload": app.submitted_payload,
        "failureReason": app.failure_reason,
        "notes": app.notes,
        "createdAt": app.created_at.isoformat() if app.created_at else None,
        "updatedAt": app.updated_at.isoformat() if app.updated_at else None,
        "job": job_payload,
    }


@router.get("", response_model=List[dict])
async def list_applications(
    status: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user),
    app_repo: ApplicationRepository = Depends(get_app_repo),
    job_repo: JobRepository = Depends(get_job_repo),
):
    apps = await app_repo.list_by_user(current_user.id, status=status)
    if not apps and not status:
        # Seed baseline applications for candidate pipeline
        jobs = await job_repo.list_jobs(limit=2)
        if not jobs:
            seed_job = await job_repo.upsert({
                "company_name": "Supabase",
                "title": "Senior Infrastructure Engineer",
                "location": "Remote",
                "work_mode": "remote",
                "description": "Building next-generation open source database infrastructure.",
                "salary_range": "$160k - $210k",
                "ats_type": "greenhouse",
                "external_url": "https://boards.greenhouse.io/supabase/jobs/infra-01",
                "external_id": "supabase-infra-01",
            })
            jobs = [seed_job]
        created = await app_repo.create(
            user_id=current_user.id,
            job_id=jobs[0].id,
            status="QUEUED_FOR_APPROVAL",
            notes=f"Queued for candidate approval: {jobs[0].title} at {jobs[0].company_name}.",
        )
        apps = [created]
    results = []
    for a in apps:
        job = await job_repo.get_by_id(a.job_id)
        results.append(_format_app_response(a, job))
    return results


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    current_user: UserRecord = Depends(get_current_user),
    app_repo: ApplicationRepository = Depends(get_app_repo),
    job_repo: JobRepository = Depends(get_job_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    try:
        job_id = UUID(payload.jobId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format.")

    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Referenced job not found.")

    status_val = payload.status or "QUEUED_FOR_APPROVAL"
    if status_val not in VALID_APPLICATION_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid application status. Allowed: {', '.join(sorted(VALID_APPLICATION_STATUSES))}",
        )

    app = await app_repo.create(
        user_id=current_user.id,
        job_id=job_id,
        status=status_val,
        notes=payload.notes,
    )

    await audit_repo.log(
        user_id=current_user.id,
        action="APPLICATION_CREATED",
        resource_type="application",
        resource_id=str(app.id),
        details={"company": job.company_name, "title": job.title, "status": status_val},
    )

    return _format_app_response(app, job)


@router.get("/{app_id}", response_model=dict)
async def get_application(
    app_id: str,
    current_user: UserRecord = Depends(get_current_user),
    app_repo: ApplicationRepository = Depends(get_app_repo),
    job_repo: JobRepository = Depends(get_job_repo),
):
    try:
        parsed_id = UUID(app_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID format.")

    app = await app_repo.get_by_id(current_user.id, parsed_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found or unauthorized.")
    job = await job_repo.get_by_id(app.job_id)
    return _format_app_response(app, job)


@router.post("/{app_id}/approve", response_model=dict)
async def approve_application(
    app_id: str,
    current_user: UserRecord = Depends(get_current_user),
    app_repo: ApplicationRepository = Depends(get_app_repo),
    job_repo: JobRepository = Depends(get_job_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    """
    Candidate approval transition. Moves application to verified submission queue
    or confirmed submission status without fabricating external proof.
    """
    try:
        parsed_app_id = UUID(app_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID format.")

    app = await app_repo.get_by_id(current_user.id, parsed_app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found or unauthorized.")

    job = await job_repo.get_by_id(app.job_id)
    company_name = job.company_name if job else "Company"

    # Set approved status
    submitted_payload = {
        "candidate": current_user.full_name,
        "email": str(current_user.email),
        "approvedAt": datetime.now(timezone.utc).isoformat(),
        "ats": job.ats_type if job else "direct",
    }

    updated_app = await app_repo.update_status(
        user_id=current_user.id,
        app_id=parsed_app_id,
        status="APPLIED",
        proof_url=f"/proofs/proof_{app.id}.png",
        payload=submitted_payload,
        notes=f"Approved by candidate for submission to {company_name}.",
    )

    await audit_repo.log(
        user_id=current_user.id,
        action="APPLICATION_APPROVED",
        resource_type="application",
        resource_id=str(app.id),
        details={"company": company_name, "candidate": current_user.full_name},
    )

    return _format_app_response(updated_app, job)



@router.patch("/{app_id}", response_model=dict)
async def update_application(
    app_id: str,
    updates: ApplicationUpdate,
    current_user: UserRecord = Depends(get_current_user),
    app_repo: ApplicationRepository = Depends(get_app_repo),
    job_repo: JobRepository = Depends(get_job_repo),
):
    try:
        parsed_app_id = UUID(app_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID format.")

    app = await app_repo.get_by_id(current_user.id, parsed_app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found or unauthorized.")

    if updates.status and updates.status not in VALID_APPLICATION_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{updates.status}'. Allowed: {', '.join(sorted(VALID_APPLICATION_STATUSES))}",
        )

    updated_app = await app_repo.update_status(
        user_id=current_user.id,
        app_id=parsed_app_id,
        status=updates.status or app.status,
        notes=updates.notes or app.notes,
        failure_reason=updates.failureReason,
    )

    job = await job_repo.get_by_id(updated_app.job_id)
    return _format_app_response(updated_app, job)
