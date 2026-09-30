from fastapi import APIRouter, Body
from typing import List, Dict, Any

router = APIRouter(prefix="/audit", tags=["Governance, Security & Audit"])

_kill_switch_active = False

_audit_logs: List[dict] = [
    {
        "id": "log_01",
        "action": "RESUME_TAILORED",
        "resourceType": "job_match",
        "resourceId": "e0000000-0000-0000-0000-000000000002",
        "details": {"company": "Vercel", "role": "Senior Full-Stack Engineer", "guardrail": "zero_fabrication_passed"},
        "timestamp": "2026-09-28T10:02:14Z"
    },
    {
        "id": "log_02",
        "action": "FORM_AUTO_APPLIED",
        "resourceType": "application",
        "resourceId": "10000000-0000-0000-0000-000000000002",
        "details": {"company": "Supabase", "ats": "greenhouse", "proofCaptured": True},
        "timestamp": "2026-09-28T14:22:00Z"
    },
    {
        "id": "log_03",
        "action": "OUTREACH_EMAIL_QUEUED",
        "resourceType": "outreach_email",
        "resourceId": "40000000-0000-0000-0000-000000000001",
        "details": {"recipient": "sarah.j@vercel.com", "step": 0, "status": "PENDING_APPROVAL"},
        "timestamp": "2026-09-30T10:00:00Z"
    }
]

@router.get("/logs", response_model=List[dict])
async def list_audit_logs():
    return _audit_logs

@router.get("/status")
async def get_system_security_status():
    global _kill_switch_active
    return {
        "killSwitchActive": _kill_switch_active,
        "tokenEncryption": "AES-256-GCM (Active)",
        "humanInTheLoop": True,
        "dailyApplyCap": 15,
        "applicationsToday": 1,
        "outreachToday": 0
    }

@router.post("/kill-switch")
async def toggle_kill_switch(active: bool = Body(..., embed=True)):
    global _kill_switch_active
    _kill_switch_active = active
    _audit_logs.insert(0, {
        "id": f"log_ks_{len(_audit_logs)+1}",
        "action": "KILL_SWITCH_ENGAGED" if active else "KILL_SWITCH_DISENGAGED",
        "resourceType": "system_governance",
        "resourceId": None,
        "details": {"activatedBy": "Alex Chen", "state": active},
        "timestamp": "2026-09-30T12:00:00Z"
    })
    return {"killSwitchActive": _kill_switch_active, "message": "Emergency kill switch updated successfully."}
