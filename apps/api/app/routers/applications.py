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
    "APPROVED",
    "READY_TO_SUBMIT",
    "SUBMITTING",
    "APPLIED",
    "NEEDS_ATTENTION",
    "FAILED",
    "INTERVIEWING",
    "OFFERED",
    "REJECTED",
    "WITHDRAWN",
}

# A candidate's approval and an external ATS submission are deliberately
# distinct events.  In particular, no regular API update may manufacture an
# APPLIED state: that state is reserved for a worker which has verified the
# provider's confirmation response and stored proof.
ALLOWED_STATUS_TRANSITIONS = {
    "SAVED": {"QUEUED_FOR_APPROVAL", "WITHDRAWN"},
    "QUEUED_FOR_APPROVAL": {"SAVED", "APPROVED", "WITHDRAWN"},
    "APPROVED": {"SUBMITTING", "NEEDS_ATTENTION", "WITHDRAWN"},
    "READY_TO_SUBMIT": {"SUBMITTING", "NEEDS_ATTENTION", "WITHDRAWN"},
    "SUBMITTING": {"APPLIED", "NEEDS_ATTENTION", "FAILED"},
    "APPLIED": {"INTERVIEWING", "OFFERED", "REJECTED", "WITHDRAWN"},
    "NEEDS_ATTENTION": {"SAVED", "QUEUED_FOR_APPROVAL", "APPROVED", "WITHDRAWN"},
    "FAILED": {"SAVED", "QUEUED_FOR_APPROVAL", "APPROVED", "WITHDRAWN"},
    "INTERVIEWING": {"OFFERED", "REJECTED", "WITHDRAWN"},
    "OFFERED": {"WITHDRAWN"},
    "REJECTED": set(),
    "WITHDRAWN": set(),
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
    "approvedAt": app.approved_at.isoformat() if app.approved_at else None,
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
    if status_val not in {"SAVED", "QUEUED_FOR_APPROVAL"}:
        raise HTTPException(
            status_code=400,
            detail="New applications must start as SAVED or QUEUED_FOR_APPROVAL.",
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
    Record the candidate's explicit approval.  This does not submit anything to
    an ATS and must not be presented as proof of an application.
    """
    try:
        parsed_app_id = UUID(app_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid application ID format.")

    app = await app_repo.get_by_id(current_user.id, parsed_app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found or unauthorized.")
    if "APPROVED" not in ALLOWED_STATUS_TRANSITIONS.get(app.status, set()):
        raise HTTPException(status_code=409, detail=f"Cannot approve an application in {app.status} status.")

    job = await job_repo.get_by_id(app.job_id)
    company_name = job.company_name if job else "Company"

    updated_app = await app_repo.update_status(
        user_id=current_user.id,
        app_id=parsed_app_id,
        status="APPROVED",
        notes=f"Approved by candidate for submission to {company_name}.",
    )

    await audit_repo.log(
        user_id=current_user.id,
        action="APPLICATION_APPROVED",
        resource_type="application",
        resource_id=str(app.id),
        details={"company": company_name, "candidate": current_user.full_name, "submission": "not_started"},
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

    next_status = updates.status or app.status
    if next_status != app.status and next_status not in ALLOWED_STATUS_TRANSITIONS.get(app.status, set()):
        raise HTTPException(status_code=409, detail=f"Cannot transition application from {app.status} to {next_status}.")
    if next_status in {"SUBMITTING", "APPLIED"}:
        raise HTTPException(
            status_code=409,
            detail=f"{next_status} can only be set by a verified submission worker.",
        )

    updated_app = await app_repo.update_status(
        user_id=current_user.id,
        app_id=parsed_app_id,
        status=next_status,
        notes=updates.notes or app.notes,
        failure_reason=updates.failureReason,
    )

    job = await job_repo.get_by_id(updated_app.job_id)
    return _format_app_response(updated_app, job)
