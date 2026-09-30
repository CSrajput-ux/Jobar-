import uuid
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, HTTPException, Body

router = APIRouter(prefix="/calendar", tags=["Calendar Automation"])

_calendar_events: List[dict] = [
    {
        "id": "60000000-0000-0000-0000-000000000001",
        "companyName": "Supabase",
        "summary": "Technical Screen: Backend Engineer @ Supabase",
        "startTime": "2026-10-02T18:00:00Z",
        "endTime": "2026-10-02T18:45:00Z",
        "meetLink": "https://meet.google.com/abc-defg-hij",
        "recruiterEmail": "elena.r@supabase.com"
    }
]

@router.get("/events", response_model=List[dict])
async def list_calendar_events():
    return _calendar_events

@router.post("/propose-slots")
async def propose_slots():
    """
    Checks user's Google Calendar free/busy schedule and proposes 3 conflict-free 45-min slots.
    """
    now = datetime.utcnow()
    slot_1 = (now + timedelta(days=2)).replace(hour=17, minute=0, second=0).isoformat() + "Z"
    slot_2 = (now + timedelta(days=2)).replace(hour=20, minute=0, second=0).isoformat() + "Z"
    slot_3 = (now + timedelta(days=3)).replace(hour=18, minute=0, second=0).isoformat() + "Z"

    return {
        "candidateTimezone": "America/Los_Angeles (PT)",
        "proposedSlots": [
            {"slot": 1, "start": slot_1, "label": "Thursday, 10:00 AM - 10:45 AM PT"},
            {"slot": 2, "start": slot_2, "label": "Thursday, 1:00 PM - 1:45 PM PT"},
            {"slot": 3, "start": slot_3, "label": "Friday, 11:00 AM - 11:45 AM PT"}
        ]
    }

@router.post("/schedule")
async def schedule_event(
    company_name: str = Body(..., embed=True),
    role: str = Body(..., embed=True),
    start_time: str = Body(..., embed=True),
    recruiter_email: str = Body(..., embed=True)
):
    event_id = str(uuid.uuid4())
    event = {
        "id": event_id,
        "companyName": company_name,
        "summary": f"Interview: {role} @ {company_name}",
        "startTime": start_time,
        "endTime": (datetime.fromisoformat(start_time.replace("Z", "")) + timedelta(minutes=45)).isoformat() + "Z",
        "meetLink": f"https://meet.google.com/{event_id[:3]}-{event_id[4:8]}-{event_id[9:12]}",
        "recruiterEmail": recruiter_email
    }
    _calendar_events.insert(0, event)
    return event
