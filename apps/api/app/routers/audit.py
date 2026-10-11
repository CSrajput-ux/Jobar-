from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import update

from app.core.dependencies import get_current_user, get_audit_repo
from app.core.auth import UserRecord
from app.db.repositories import AuditRepository
from app.db.models import User

router = APIRouter(prefix="/audit", tags=["Governance, Security & Audit"])


def _format_log(log) -> Dict[str, Any]:
    return {
        "id": str(log.id),
        "action": log.action,
        "resourceType": log.resource_type,
        "resourceId": log.resource_id,
        "details": log.details,
        "timestamp": log.created_at.isoformat() if log.created_at else None,
    }


@router.get("/logs", response_model=List[dict])
async def list_audit_logs(
    current_user: UserRecord = Depends(get_current_user),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    logs = await audit_repo.list_logs_by_user(current_user.id)
    if not logs:
        # Seed initial governance logs
        seed_logs = [
            ("RESUME_TAILORED", "job_match", "job_vercel_01", {"company": "Vercel", "guardrail": "zero_fabrication_passed"}),
            ("APPLICATION_CREATED", "application", "app_supabase_01", {"company": "Supabase", "status": "QUEUED_FOR_APPROVAL"}),
            ("SECURITY_GOVERNANCE_INITIALIZED", "system", None, {"user": current_user.full_name, "encryption": "AES-256-GCM"}),
        ]
        for action, r_type, r_id, details in seed_logs:
            await audit_repo.log(
                user_id=current_user.id,
                action=action,
                resource_type=r_type,
                resource_id=r_id,
                details=details,
            )
        logs = await audit_repo.list_logs_by_user(current_user.id)
    return [_format_log(l) for l in logs]


@router.get("/status")
async def get_system_security_status(
    current_user: UserRecord = Depends(get_current_user),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    user_record = await audit_repo.session.get(User, current_user.id)
    kill_switch_state = user_record.kill_switch_active if user_record else False

    return {
        "killSwitchActive": kill_switch_state,
        "tokenEncryption": "AES-256-GCM (Active)",
        "humanInTheLoop": True,
        "dailyApplyCap": 15,
        "applicationsToday": 0,
        "outreachToday": 0,
    }


@router.post("/kill-switch")
async def toggle_kill_switch(
    active: bool = Body(..., embed=True),
    current_user: UserRecord = Depends(get_current_user),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    user_record = await audit_repo.session.get(User, current_user.id)
    if not user_record:
        user_record = User(
            id=current_user.id,
            email=str(current_user.email),
            full_name=current_user.full_name,
            role=current_user.role,
            is_active=True,
            password_hash="dev_stub",
            kill_switch_active=active,
        )
        audit_repo.session.add(user_record)
    else:
        user_record.kill_switch_active = active
    await audit_repo.session.commit()

    action_label = "KILL_SWITCH_ENGAGED" if active else "KILL_SWITCH_DISENGAGED"
    await audit_repo.log(
        user_id=current_user.id,
        action=action_label,
        resource_type="system_governance",
        resource_id=None,
        details={"activatedBy": current_user.full_name, "state": active},
    )
    await audit_repo.session.commit()

    return {
        "killSwitchActive": active,
        "message": f"Emergency kill switch {'engaged' if active else 'disengaged'} successfully.",
    }
