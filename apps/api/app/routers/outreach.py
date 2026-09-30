import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body
from app.schemas.outreach import ContactResponse, OutreachEmailCreate, OutreachEmailResponse
from app.services.ai_service import ai_service
from app.routers.jobs import _jobs_cache

router = APIRouter(prefix="/outreach", tags=["Cold Email & Outreach"])

_contacts_cache: List[dict] = [
    {
        "id": "20000000-0000-0000-0000-000000000001",
        "companyId": "d0000000-0000-0000-0000-000000000002",
        "companyName": "Vercel",
        "fullName": "Sarah Jenkins",
        "email": "sarah.j@vercel.com",
        "roleTitle": "Senior Technical Recruiter (Engineering)",
        "linkedinUrl": "https://linkedin.com/in/sarah-jenkins-tech",
        "isVerified": True
    },
    {
        "id": "20000000-0000-0000-0000-000000000002",
        "companyId": "d0000000-0000-0000-0000-000000000001",
        "companyName": "Linear",
        "fullName": "Marcus Vance",
        "email": "marcus@linear.app",
        "roleTitle": "Head of Engineering Talent",
        "linkedinUrl": "https://linkedin.com/in/marcus-vance-linear",
        "isVerified": True
    },
    {
        "id": "20000000-0000-0000-0000-000000000003",
        "companyId": "d0000000-0000-0000-0000-000000000003",
        "companyName": "Supabase",
        "fullName": "Elena Rostova",
        "email": "elena.r@supabase.com",
        "roleTitle": "Lead Tech Recruiter",
        "linkedinUrl": "https://linkedin.com/in/elena-rostova",
        "isVerified": True
    }
]

_emails_cache: List[dict] = [
    {
        "id": "40000000-0000-0000-0000-000000000001",
        "campaignId": "30000000-0000-0000-0000-000000000001",
        "sequenceStep": 0,
        "contactName": "Sarah Jenkins",
        "contactEmail": "sarah.j@vercel.com",
        "companyName": "Vercel",
        "subject": "Building AI web applications @ Vercel — Alex Chen",
        "bodyText": "Hi Sarah,\n\nI noticed Vercel is scaling the AI Platforms team. Over the past 4 years, I have architected high-performance Next.js systems and distributed LLM pipelines, including an open-source queue gateway that handles 45M daily events.\n\nI submitted an application for the Senior Full-Stack role and would welcome 10 minutes to connect if my background aligns with your roadmap.\n\nBest regards,\nAlex Chen | https://github.com/alexchen\n\n---\nReply 'unsubscribe' to opt out.",
        "status": "PENDING_APPROVAL",
        "scheduledSendAt": "2026-09-30T15:00:00Z",
        "sentAt": None
    }
]

@router.get("/contacts", response_model=List[ContactResponse])
async def list_contacts():
    return _contacts_cache

@router.get("/emails", response_model=List[dict])
async def list_emails():
    return _emails_cache

@router.post("/generate", response_model=dict)
async def generate_outreach_email(payload: OutreachEmailCreate):
    contact = next((c for c in _contacts_cache if c["id"] == payload.contactId), None)
    job = next((j for j in _jobs_cache if j["id"] == payload.jobId), None)
    
    if not contact or not job:
        raise HTTPException(status_code=404, detail="Contact or Job not found")

    generated = await ai_service.generate_cold_outreach(
        candidate_name="Alex Chen",
        recruiter_name=contact["fullName"],
        company_name=contact["companyName"],
        role_title=job["title"],
        tone=payload.tone or "confident_professional"
    )

    new_email = {
        "id": str(uuid.uuid4()),
        "campaignId": str(uuid.uuid4()),
        "sequenceStep": 0,
        "contactName": contact["fullName"],
        "contactEmail": contact["email"],
        "companyName": contact["companyName"],
        "subject": generated["subject"],
        "bodyText": generated["bodyText"],
        "status": "PENDING_APPROVAL",
        "scheduledSendAt": datetime.utcnow().isoformat() + "Z",
        "sentAt": None
    }
    _emails_cache.insert(0, new_email)
    return new_email

@router.post("/send/{email_id}", response_model=dict)
async def send_email(email_id: str):
    email = next((e for e in _emails_cache if e["id"] == email_id), None)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    email["status"] = "SENT"
    email["sentAt"] = datetime.utcnow().isoformat() + "Z"
    return email
