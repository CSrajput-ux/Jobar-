from __future__ import annotations

import io
from typing import Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status

from app.schemas.profile import StructuredProfileSchema, PreferencesSchema, CommonQASchema
from app.services.ai_service import ai_service
from app.core.dependencies import get_current_user, get_profile_repo
from app.core.auth import UserRecord
from app.db.repositories import ProfileRepository

router = APIRouter(prefix="/profile", tags=["Profile & Onboarding"])

MAX_CV_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
ALLOWED_CV_EXTENSIONS = {".pdf", ".txt", ".md", ".json", ".docx"}


@router.get("", response_model=StructuredProfileSchema)
async def get_profile(
    current_user: UserRecord = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    profile = await profile_repo.get_or_create(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_email=str(current_user.email),
    )
    return {
        "headline": profile.headline or "Software Engineer",
        "summary": profile.summary or f"Profile for {current_user.full_name}.",
        "phone": profile.phone,
        "location": profile.location or "Remote",
        "linkedinUrl": profile.linkedin_url,
        "githubUrl": profile.github_url,
        "skills": profile.skills or {"technical": [], "frameworks": [], "tools": [], "languages": []},
        "experience": profile.experience or [],
        "education": profile.education or [],
        "projects": profile.projects or [],
    }


@router.post("/upload-cv", response_model=StructuredProfileSchema)
async def upload_cv(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    current_user: UserRecord = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    text_content = (raw_text or "").strip()
    if file:
        filename = (file.filename or "").lower()
        if not any(filename.endswith(ext) for ext in ALLOWED_CV_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed extensions: {', '.join(sorted(ALLOWED_CV_EXTENSIONS))}",
            )

        content_bytes = await file.read()
        if len(content_bytes) > MAX_CV_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uploaded file exceeds maximum size limit of {MAX_CV_FILE_SIZE // (1024 * 1024)}MB.",
            )

        try:
            text_content = content_bytes.decode("utf-8", errors="ignore")
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read CV content: {exc}",
            )

    if not text_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No CV content provided. Please upload a file or submit raw text.",
        )

    parsed = await ai_service.parse_cv_text(text_content)
    # Update persisted database record for this authenticated user
    updated = await profile_repo.update_profile(
        user_id=current_user.id,
        data={
            "headline": parsed.get("headline", "Software Engineer"),
            "summary": parsed.get("summary", ""),
            "phone": parsed.get("phone"),
            "location": parsed.get("location", "Remote"),
            "linkedin_url": parsed.get("linkedinUrl"),
            "github_url": parsed.get("githubUrl"),
            "skills": parsed.get("skills", {}),
            "experience": parsed.get("experience", []),
            "education": parsed.get("education", []),
            "projects": parsed.get("projects", []),
        },
    )
    return {
        "headline": updated.headline,
        "summary": updated.summary or "",
        "phone": updated.phone,
        "location": updated.location,
        "linkedinUrl": updated.linkedin_url,
        "githubUrl": updated.github_url,
        "skills": updated.skills,
        "experience": updated.experience,
        "education": updated.education,
        "projects": updated.projects,
    }


@router.put("", response_model=StructuredProfileSchema)
async def update_profile(
    profile_data: StructuredProfileSchema,
    current_user: UserRecord = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    updated = await profile_repo.update_profile(
        user_id=current_user.id,
        data={
            "headline": profile_data.headline,
            "summary": profile_data.summary,
            "phone": profile_data.phone,
            "location": profile_data.location,
            "linkedin_url": profile_data.linkedinUrl,
            "github_url": profile_data.githubUrl,
            "skills": profile_data.skills,
            "experience": [e.model_dump() for e in profile_data.experience],
            "education": [e.model_dump() for e in profile_data.education],
            "projects": [p.model_dump() for p in profile_data.projects],
        },
    )
    return {
        "headline": updated.headline,
        "summary": updated.summary or "",
        "phone": updated.phone,
        "location": updated.location,
        "linkedinUrl": updated.linkedin_url,
        "githubUrl": updated.github_url,
        "skills": updated.skills,
        "experience": updated.experience,
        "education": updated.education,
        "projects": updated.projects,
    }


@router.get("/preferences", response_model=PreferencesSchema)
async def get_preferences(
    current_user: UserRecord = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    prefs = await profile_repo.get_preferences(current_user.id)
    return {
        "targetRoles": prefs.target_roles or ["Software Engineer"],
        "seniorityLevels": prefs.seniority_levels or ["Mid", "Senior"],
        "locations": prefs.locations or ["Remote"],
        "workModes": prefs.work_modes or ["remote"],
        "minSalaryUsd": prefs.min_salary_usd,
        "visaSponsorshipRequired": prefs.visa_sponsorship_required,
        "blacklistedCompanies": prefs.blacklisted_companies or [],
        "targetIndustries": prefs.target_industries or [],
        "applyMode": prefs.apply_mode,
        "dailyApplyCap": prefs.daily_apply_cap,
        "minMatchScore": prefs.min_match_score,
    }


@router.put("/preferences", response_model=PreferencesSchema)
async def update_preferences(
    prefs_data: PreferencesSchema,
    current_user: UserRecord = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    updated = await profile_repo.update_preferences(
        user_id=current_user.id,
        data={
            "target_roles": prefs_data.targetRoles,
            "seniority_levels": prefs_data.seniorityLevels,
            "locations": prefs_data.locations,
            "work_modes": prefs_data.workModes,
            "min_salary_usd": prefs_data.minSalaryUsd,
            "visa_sponsorship_required": prefs_data.visaSponsorshipRequired,
            "blacklisted_companies": prefs_data.blacklistedCompanies,
            "target_industries": prefs_data.targetIndustries,
            "apply_mode": prefs_data.applyMode,
            "daily_apply_cap": prefs_data.dailyApplyCap,
            "min_match_score": prefs_data.minMatchScore,
        },
    )
    return {
        "targetRoles": updated.target_roles,
        "seniorityLevels": updated.seniority_levels,
        "locations": updated.locations,
        "workModes": updated.work_modes,
        "minSalaryUsd": updated.min_salary_usd,
        "visaSponsorshipRequired": updated.visa_sponsorship_required,
        "blacklistedCompanies": updated.blacklisted_companies,
        "targetIndustries": updated.target_industries,
        "applyMode": updated.apply_mode,
        "dailyApplyCap": updated.daily_apply_cap,
        "minMatchScore": updated.min_match_score,
    }


@router.get("/common-qa", response_model=CommonQASchema)
async def get_common_qa(
    current_user: UserRecord = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    qa = await profile_repo.get_common_qa(current_user.id)
    return {
        "noticePeriodDays": qa.notice_period_days,
        "workAuthStatus": qa.work_auth_status,
        "requiresSponsorship": qa.requires_sponsorship,
        "expectedSalaryUsd": qa.expected_salary_usd,
        "whyCompanyDefault": qa.why_company_default,
        "customAnswers": qa.custom_answers or {},
    }


@router.put("/common-qa", response_model=CommonQASchema)
async def update_common_qa(
    qa_data: CommonQASchema,
    current_user: UserRecord = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
):
    updated = await profile_repo.update_common_qa(
        user_id=current_user.id,
        data={
            "notice_period_days": qa_data.noticePeriodDays,
            "work_auth_status": qa_data.workAuthStatus,
            "requires_sponsorship": qa_data.requiresSponsorship,
            "expected_salary_usd": qa_data.expectedSalaryUsd,
            "why_company_default": qa_data.whyCompanyDefault,
            "custom_answers": qa_data.customAnswers,
        },
    )
    return {
        "noticePeriodDays": updated.notice_period_days,
        "workAuthStatus": updated.work_auth_status,
        "requiresSponsorship": updated.requires_sponsorship,
        "expectedSalaryUsd": updated.expected_salary_usd,
        "whyCompanyDefault": updated.why_company_default,
        "customAnswers": updated.custom_answers,
    }
