import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body
from app.schemas.apply import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.routers.jobs import _jobs_cache

router = APIRouter(prefix="/applications", tags=["Applications & Pipeline"])

_applications_cache: List[dict] = [
    {
        "id": "10000000-0000-0000-0000-000000000001",
        "userId": "a0000000-0000-0000-0000-000000000001",
        "jobId": "e0000000-0000-0000-0000-000000000002",
        "status": "QUEUED_FOR_APPROVAL",
        "appliedAt": None,
        "proofScreenshotUrl": None,
        "submittedPayload": None,
        "failureReason": None,
        "notes": "96% match. Tailored resume & cover letter prepared for Vercel AI Platforms.",
        "createdAt": "2026-09-28T10:00:00Z",
        "updatedAt": "2026-09-28T10:00:00Z"
    },
    {
        "id": "10000000-0000-0000-0000-000000000002",
        "userId": "a0000000-0000-0000-0000-000000000001",
        "jobId": "e0000000-0000-0000-0000-000000000003",
        "status": "APPLIED",
        "appliedAt": "2026-09-28T14:22:00Z",
        "proofScreenshotUrl": "https://storage.jobpilot.dev/proofs/supabase_application_proof.png",
        "submittedPayload": {
            "fullName": "Alex Chen",
            "email": "alex.chen.dev@gmail.com",
            "resume": "Alex_Chen_Tailored_Supabase.pdf",
            "workAuth": "Authorized without sponsorship"
        },
        "failureReason": None,
        "notes": "Submitted via Greenhouse API automation. Confirmation page verified.",
        "createdAt": "2026-09-28T14:20:00Z",
        "updatedAt": "2026-09-28T14:22:00Z"
    },
    {
        "id": "10000000-0000-0000-0000-000000000003",
        "userId": "a0000000-0000-0000-0000-000000000001",
        "jobId": "e0000000-0000-0000-0000-000000000001",
        "status": "SAVED",
        "appliedAt": None,
        "proofScreenshotUrl": None,
        "submittedPayload": None,
        "failureReason": None,
        "notes": "Linear Staff Systems opening. High-relevance distributed architecture role.",
        "createdAt": "2026-09-29T09:00:00Z",
        "updatedAt": "2026-09-29T09:00:00Z"
    }
]

@router.get("", response_model=List[dict])
async def list_applications(status: Optional[str] = None):
    # Enrich with job details for Kanban display
    jobs_map = {j["id"]: j for j in _jobs_cache}
    enriched = []
    for app in _applications_cache:
        if status and app["status"] != status:
            continue
        copy_app = dict(app)
        copy_app["job"] = jobs_map.get(app["jobId"])
        enriched.append(copy_app)
    return enriched

@router.post("", response_model=dict)
async def create_application(payload: ApplicationCreate):
    # Check if already exists
    for app in _applications_cache:
        if app["jobId"] == payload.jobId:
            return app

    new_app = {
        "id": str(uuid.uuid4()),
        "userId": "a0000000-0000-0000-0000-000000000001",
        "jobId": payload.jobId,
        "status": payload.status or "QUEUED_FOR_APPROVAL",
        "appliedAt": None,
        "proofScreenshotUrl": None,
        "submittedPayload": None,
        "failureReason": None,
        "notes": payload.notes or "Queued by user",
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "updatedAt": datetime.utcnow().isoformat() + "Z"
    }
    _applications_cache.insert(0, new_app)
    return new_app

@router.post("/{app_id}/approve", response_model=dict)
async def approve_application(app_id: str):
    """
    1-Click Approval: moves an application from QUEUED_FOR_APPROVAL to APPLIED,
    captures proof and audit log.
    """
    app = next((a for a in _applications_cache if a["id"] == app_id), None)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    job = next((j for j in _jobs_cache if j["id"] == app["jobId"]), None)
    company_name = job["companyName"] if job else "Company"

    app["status"] = "APPLIED"
    app["appliedAt"] = datetime.utcnow().isoformat() + "Z"
    app["proofScreenshotUrl"] = f"https://storage.jobpilot.dev/proofs/{company_name.lower()}_apply_proof.png"
    app["submittedPayload"] = {
        "candidate": "Alex Chen",
        "email": "alex.chen.dev@gmail.com",
        "resume": f"Alex_Chen_Tailored_{company_name}.pdf",
        "timestamp": app["appliedAt"],
        "ats": job.get("atsType", "greenhouse") if job else "ats"
    }
    app["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    return app

@router.patch("/{app_id}", response_model=dict)
async def update_application(app_id: str, updates: ApplicationUpdate):
    app = next((a for a in _applications_cache if a["id"] == app_id), None)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if updates.status:
        app["status"] = updates.status
    if updates.notes:
        app["notes"] = updates.notes
    if updates.failureReason:
        app["failureReason"] = updates.failureReason
    app["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    return app
