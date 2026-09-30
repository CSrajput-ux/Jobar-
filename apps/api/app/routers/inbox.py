from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from app.services.ai_service import ai_service

router = APIRouter(prefix="/inbox", tags=["Inbox Intelligence"])

_threads_cache: List[dict] = [
    {
        "id": "50000000-0000-0000-0000-000000000001",
        "userId": "a0000000-0000-0000-0000-000000000001",
        "companyName": "Supabase",
        "gmailThreadId": "thread_supabase_recruiter_01",
        "subject": "Invitation to Interview: Backend Engineer @ Supabase",
        "fromAddress": "careers@supabase.com",
        "snippet": "Hi Alex, thanks for your application. The engineering team reviewed your background with pgvector and would love to schedule a 30-minute technical intro...",
        "classification": "INTERVIEW_INVITE",
        "confidence": 0.98,
        "actionRequired": True,
        "lastMessageAt": "2026-09-30T10:15:00Z",
        "proposedReply": "Hi, thank you for reaching out! I would love to connect. I am generally available this Thursday and Friday between 10am-4pm PT. Looking forward to speaking with the team!"
    },
    {
        "id": "50000000-0000-0000-0000-000000000002",
        "userId": "a0000000-0000-0000-0000-000000000001",
        "companyName": "Stripe",
        "gmailThreadId": "thread_stripe_rejection_02",
        "subject": "Update regarding your application at Stripe",
        "fromAddress": "talent@stripe.com",
        "snippet": "Thank you for taking the time to speak with our team. While we were impressed by your background, we have decided to move forward with other candidates...",
        "classification": "REJECTION",
        "confidence": 0.99,
        "actionRequired": False,
        "lastMessageAt": "2026-09-29T16:40:00Z",
        "proposedReply": None
    }
]

@router.get("/threads", response_model=List[dict])
async def list_threads():
    return _threads_cache

@router.post("/classify")
async def classify_message(
    subject: str = Body(..., embed=True),
    body: str = Body(..., embed=True),
    sender: str = Body(..., embed=True)
):
    classification = await ai_service.classify_inbound_email(subject, body, sender)
    return classification

@router.post("/threads/{thread_id}/reply")
async def reply_thread(thread_id: str, reply_text: str = Body(..., embed=True)):
    thread = next((t for t in _threads_cache if t["id"] == thread_id), None)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    thread["actionRequired"] = False
    return {
        "status": "sent",
        "threadId": thread_id,
        "reply": reply_text
    }
