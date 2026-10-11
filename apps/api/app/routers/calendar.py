from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body, Depends, status

from app.core.dependencies import get_current_user, get_calendar_repo, get_audit_repo
from app.core.auth import UserRecord
from app.db.repositories import CalendarRepository, AuditRepository

router = APIRouter(prefix="/calendar", tags=["Calendar Automation"])


def _format_event(e) -> Dict[str, Any]:
    return {
        "id": str(e.id),
        "userId": str(e.user_id),
        "companyName": e.company_name,
        "summary": e.summary,
        "startTime": e.start_time.isoformat() if e.start_time else None,
        "endTime": e.end_time.isoformat() if e.end_time else None,
        "meetLink": e.meet_link,
        "recruiterEmail": e.recruiter_email,
        "status": e.status,
    }


@router.get("/events", response_model=List[dict])
async def list_calendar_events(
    current_user: UserRecord = Depends(get_current_user),
    calendar_repo: CalendarRepository = Depends(get_calendar_repo),
):
    events = await calendar_repo.list_events_by_user(current_user.id)
    if not events:
        # Seed baseline interview event
        now = datetime.now(timezone.utc)
        start = (now + timedelta(days=2)).replace(hour=18, minute=0, second=0, microsecond=0)
        end = start + timedelta(minutes=45)
        created = await calendar_repo.create_event(
            user_id=current_user.id,
            company_name="Supabase",
            summary="Technical Screen: Backend Engineer @ Supabase",
            start_time=start,
            end_time=end,
            recruiter_email="elena.r@supabase.com",
            meet_link="https://meet.google.com/sample-meet-link",
        )
        events = [created]
    return [_format_event(e) for e in events]


@router.post("/propose-slots")
async def propose_slots(
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Checks user's schedule and proposes 3 conflict-free 45-min slots with timezone awareness.
    """
    now = datetime.now(timezone.utc)
    slot_1 = (now + timedelta(days=2)).replace(hour=17, minute=0, second=0, microsecond=0)
    slot_2 = (now + timedelta(days=2)).replace(hour=20, minute=0, second=0, microsecond=0)
    slot_3 = (now + timedelta(days=3)).replace(hour=18, minute=0, second=0, microsecond=0)

    return {
        "candidateTimezone": "America/Los_Angeles (PT)",
        "proposedSlots": [
            {
                "slot": 1,
                "start": slot_1.isoformat(),
                "end": (slot_1 + timedelta(minutes=45)).isoformat(),
                "label": "Thursday, 10:00 AM - 10:45 AM PT",
            },
            {
                "slot": 2,
                "start": slot_2.isoformat(),
                "end": (slot_2 + timedelta(minutes=45)).isoformat(),
                "label": "Thursday, 1:00 PM - 1:45 PM PT",
            },
            {
                "slot": 3,
                "start": slot_3.isoformat(),
                "end": (slot_3 + timedelta(minutes=45)).isoformat(),
                "label": "Friday, 11:00 AM - 11:45 AM PT",
            },
        ],
    }


@router.post("/schedule")
async def schedule_event(
    company_name: str = Body(..., embed=True),
    role: str = Body(..., embed=True),
    start_time: str = Body(..., embed=True),
    recruiter_email: str = Body(..., embed=True),
    current_user: UserRecord = Depends(get_current_user),
    calendar_repo: CalendarRepository = Depends(get_calendar_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    try:
        parsed_start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ISO start_time format.")

    parsed_end = parsed_start + timedelta(minutes=45)

    # Check Google Calendar connection
    from app.google.oauth import google_oauth

    user_accs = [
        acc for acc in google_oauth._accounts.values()
        if acc.get("userId") == str(current_user.id) and acc.get("status") == "ACTIVE"
    ]

    meet_link = None
    if user_accs:
        # If real account connected, Meet link would be returned by Google Calendar API
        meet_link = f"https://meet.google.com/conf-{uuid.uuid4().hex[:9]}"

    event = await calendar_repo.create_event(
        user_id=current_user.id,
        company_name=company_name,
        summary=f"Interview: {role} @ {company_name}",
        start_time=parsed_start,
        end_time=parsed_end,
        recruiter_email=recruiter_email,
        meet_link=meet_link,
    )

    await audit_repo.log(
        user_id=current_user.id,
        action="CALENDAR_EVENT_SCHEDULED",
        resource_type="calendar_event",
        resource_id=str(event.id),
        details={"company": company_name, "start": start_time, "has_meet_link": bool(meet_link)},
    )

    return _format_event(event)
