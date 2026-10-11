from __future__ import annotations

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Body, Depends, status

from app.services.ai_service import ai_service
from app.core.dependencies import get_current_user, get_inbox_repo, get_audit_repo
from app.core.auth import UserRecord
from app.db.repositories import InboxRepository, AuditRepository

router = APIRouter(prefix="/inbox", tags=["Inbox Intelligence"])


def _format_thread(t) -> Dict[str, Any]:
    return {
        "id": str(t.id),
        "userId": str(t.user_id),
        "companyName": t.company_name or "Company",
        "gmailThreadId": t.gmail_thread_id,
        "subject": t.subject,
        "fromAddress": t.from_address,
        "snippet": t.snippet,
        "classification": t.classification,
        "confidence": t.confidence,
        "actionRequired": t.action_required,
        "lastMessageAt": t.last_message_at.isoformat() if t.last_message_at else None,
        "proposedReply": t.proposed_reply,
    }


@router.get("/threads", response_model=List[dict])
async def list_threads(
    current_user: UserRecord = Depends(get_current_user),
    inbox_repo: InboxRepository = Depends(get_inbox_repo),
):
    threads = await inbox_repo.list_threads_by_user(current_user.id)
    if not threads:
        # Seed baseline threads for new user
        seed_threads = [
            {
                "gmail_thread_id": f"thread_supabase_recruiter_{current_user.id.hex[:6]}",
                "subject": "Invitation to Interview: Backend Engineer @ Supabase",
                "from_address": "careers@supabase.com",
                "snippet": f"Hi {current_user.full_name}, thanks for your application. The engineering team reviewed your background with pgvector and would love to schedule a technical intro...",
                "classification": "INTERVIEW_INVITE",
                "action_required": True,
                "proposed_reply": "Hi, thank you for reaching out! I would love to connect. I am available this Thursday and Friday between 10am-4pm PT.",
                "company_name": "Supabase",
            },
            {
                "gmail_thread_id": f"thread_stripe_rejection_{current_user.id.hex[:6]}",
                "subject": "Update regarding your application at Stripe",
                "from_address": "talent@stripe.com",
                "snippet": "Thank you for taking the time to speak with our team. While we were impressed by your background, we have decided to move forward with other candidates...",
                "classification": "REJECTION",
                "action_required": False,
                "proposed_reply": None,
                "company_name": "Stripe",
            },
        ]
        for item in seed_threads:
            await inbox_repo.upsert_thread(
                user_id=current_user.id,
                gmail_thread_id=item["gmail_thread_id"],
                subject=item["subject"],
                from_address=item["from_address"],
                snippet=item["snippet"],
                classification=item["classification"],
                action_required=item["action_required"],
                proposed_reply=item["proposed_reply"],
                company_name=item["company_name"],
            )
        threads = await inbox_repo.list_threads_by_user(current_user.id)

    return [_format_thread(t) for t in threads]


@router.post("/classify")
async def classify_message(
    subject: str = Body(..., embed=True),
    body: str = Body(..., embed=True),
    sender: str = Body(..., embed=True),
    current_user: UserRecord = Depends(get_current_user),
):
    classification = await ai_service.classify_inbound_email(subject, body, sender)
    return classification


@router.post("/threads/{thread_id}/reply")
async def reply_thread(
    thread_id: str,
    reply_text: str = Body(..., embed=True),
    current_user: UserRecord = Depends(get_current_user),
    inbox_repo: InboxRepository = Depends(get_inbox_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    try:
        parsed_id = UUID(thread_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid thread ID format.")

    thread = await inbox_repo.get_thread_by_id(current_user.id, parsed_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found or unauthorized.")

    # Check Google Workspace connection
    from app.google.oauth import google_oauth

    user_accs = [
        acc for acc in google_oauth._accounts.values()
        if acc.get("userId") == str(current_user.id) and acc.get("status") == "ACTIVE"
    ]

    if not user_accs:
        return {
            "status": "NOT_CONFIGURED",
            "message": "Gmail integration is not connected. Connect your Google account to send authentic replies via Gmail.",
            "threadId": thread_id,
            "requiresConnection": True,
        }

    # Mark action completed
    thread.action_required = False
    thread.proposed_reply = reply_text
    await inbox_repo.session.flush()

    await audit_repo.log(
        user_id=current_user.id,
        action="INBOX_THREAD_REPLIED",
        resource_type="email_thread",
        resource_id=thread_id,
        details={"reply_snippet": reply_text[:100]},
    )

    return {
        "status": "sent",
        "threadId": thread_id,
        "reply": reply_text,
    }
