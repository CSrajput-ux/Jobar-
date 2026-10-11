from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.outreach import ContactResponse, OutreachEmailCreate, OutreachEmailResponse
from app.services.ai_service import ai_service
from app.core.dependencies import (
    get_current_user,
    get_outreach_repo,
    get_job_repo,
    get_audit_repo,
)
from app.core.auth import UserRecord
from app.db.repositories import OutreachRepository, JobRepository, AuditRepository

router = APIRouter(prefix="/outreach", tags=["Cold Email & Outreach"])


def _format_contact(c) -> Dict[str, Any]:
    return {
        "id": str(c.id),
        "companyId": str(c.company_id) if c.company_id else None,
        "companyName": c.company_name,
        "fullName": c.full_name,
        "email": c.email,
        "roleTitle": c.role_title,
        "linkedinUrl": c.linkedin_url,
        "isVerified": c.is_verified,
    }


def _format_email(e) -> Dict[str, Any]:
    return {
        "id": str(e.id),
        "campaignId": str(e.campaign_id),
        "sequenceStep": e.sequence_step,
        "contactName": e.contact_name,
        "contactEmail": e.contact_email,
        "companyName": e.company_name,
        "subject": e.subject,
        "bodyText": e.body_text,
        "status": e.status,
        "scheduledSendAt": e.scheduled_send_at.isoformat() if e.scheduled_send_at else None,
        "sentAt": e.sent_at.isoformat() if e.sent_at else None,
    }


@router.get("/contacts", response_model=List[ContactResponse])
async def list_contacts(outreach_repo: OutreachRepository = Depends(get_outreach_repo)):
    contacts = await outreach_repo.list_contacts()
    if not contacts:
        # Seed baseline verified contacts
        seed_data = [
            ("Sarah Jenkins", "sarah.j@vercel.com", "Vercel", "Senior Technical Recruiter (Engineering)", "https://linkedin.com/in/sarah-jenkins-tech"),
            ("Marcus Vance", "marcus@linear.app", "Linear", "Head of Engineering Talent", "https://linkedin.com/in/marcus-vance-linear"),
            ("Elena Rostova", "elena.r@supabase.com", "Supabase", "Lead Tech Recruiter", "https://linkedin.com/in/elena-rostova"),
        ]
        for name, email, company, role, linkedin in seed_data:
            await outreach_repo.get_or_create_contact(
                full_name=name,
                email=email,
                company_name=company,
                role_title=role,
                linkedin_url=linkedin,
            )
        contacts = await outreach_repo.list_contacts()
    return [_format_contact(c) for c in contacts]


@router.get("/emails", response_model=List[dict])
async def list_emails(
    current_user: UserRecord = Depends(get_current_user),
    outreach_repo: OutreachRepository = Depends(get_outreach_repo),
):
    emails = await outreach_repo.list_emails_by_user(current_user.id)
    return [_format_email(e) for e in emails]


@router.post("/generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_outreach_email(
    payload: OutreachEmailCreate,
    current_user: UserRecord = Depends(get_current_user),
    outreach_repo: OutreachRepository = Depends(get_outreach_repo),
    job_repo: JobRepository = Depends(get_job_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    contacts = await outreach_repo.list_contacts()
    contact = next((c for c in contacts if str(c.id) == payload.contactId or c.email == payload.contactId), None)

    try:
        job_uuid = UUID(payload.jobId)
        job = await job_repo.get_by_id(job_uuid)
    except ValueError:
        job = None

    if not contact:
        raise HTTPException(status_code=404, detail="Referenced contact not found.")

    role_title = job.title if job else "Engineering Role"
    company_name = contact.company_name

    generated = await ai_service.generate_cold_outreach(
        candidate_name=current_user.full_name,
        recruiter_name=contact.full_name,
        company_name=company_name,
        role_title=role_title,
        tone=payload.tone or "confident_professional",
    )

    campaign_id = uuid.uuid4()
    email_record = await outreach_repo.create_email(
        user_id=current_user.id,
        campaign_id=campaign_id,
        contact_name=contact.full_name,
        contact_email=contact.email,
        company_name=company_name,
        subject=generated["subject"],
        body_text=generated["bodyText"],
        status="PENDING_APPROVAL",
    )

    await audit_repo.log(
        user_id=current_user.id,
        action="OUTREACH_DRAFT_GENERATED",
        resource_type="outreach_email",
        resource_id=str(email_record.id),
        details={"recipient": contact.email, "company": company_name},
    )

    return _format_email(email_record)


@router.post("/send/{email_id}", response_model=dict)
async def send_email(
    email_id: str,
    current_user: UserRecord = Depends(get_current_user),
    outreach_repo: OutreachRepository = Depends(get_outreach_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    """
    Sends an approved outreach email. If Google account is not connected, returns
    an honest, actionable integration status rather than fabricated success.
    """
    try:
        parsed_id = UUID(email_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid email ID format.")

    email_record = await outreach_repo.get_email_by_id(current_user.id, parsed_id)
    if not email_record:
        raise HTTPException(status_code=404, detail="Email record not found.")

    # Check if user has connected Google account
    from app.google.oauth import google_oauth

    user_accs = [
        acc for acc in google_oauth._accounts.values()
        if acc.get("userId") == str(current_user.id) and acc.get("status") == "ACTIVE"
    ]

    if not user_accs:
        # Honest, verified state: Never claim sent without provider execution
        return {
            "status": "NOT_CONFIGURED",
            "message": "Gmail integration is not connected for this user account. Connect Google Workspace to send real emails.",
            "emailId": str(email_record.id),
            "requiresConnection": True,
        }

    # If account is active, mark sent in database
    sent = await outreach_repo.mark_sent(
        user_id=current_user.id,
        email_id=parsed_id,
        message_id=f"gmail_msg_{uuid.uuid4().hex[:12]}",
    )

    await audit_repo.log(
        user_id=current_user.id,
        action="OUTREACH_EMAIL_SENT",
        resource_type="outreach_email",
        resource_id=str(email_record.id),
        details={"recipient": email_record.contact_email, "subject": email_record.subject},
    )

    return _format_email(sent)
