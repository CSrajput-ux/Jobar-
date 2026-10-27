from __future__ import annotations

import io
import zipfile
from pathlib import Path
from xml.etree import ElementTree
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status

from app.schemas.profile import StructuredProfileSchema, PreferencesSchema, CommonQASchema
from app.services.ai_service import ai_service
from app.core.dependencies import (
    get_current_user,
    get_profile_repo,
    get_job_repo,
    get_match_repo,
    get_app_repo,
    get_audit_repo,
)
from app.core.auth import UserRecord
from app.db.repositories import (
    ProfileRepository,
    JobRepository,
    MatchRepository,
    ApplicationRepository,
    AuditRepository,
)

router = APIRouter(prefix="/profile", tags=["Profile & Onboarding"])

MAX_CV_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
ALLOWED_CV_EXTENSIONS = {".pdf", ".txt", ".md", ".json", ".docx"}


def _profile_response(profile) -> Dict[str, Any]:
    return {
        "headline": profile.headline or "Software Engineer",
        "summary": profile.summary or "",
        "phone": profile.phone,
        "location": profile.location or "Remote",
        "linkedinUrl": profile.linkedin_url,
        "githubUrl": profile.github_url,
        "skills": profile.skills or {"technical": [], "frameworks": [], "tools": [], "languages": []},
        "experience": profile.experience or [],
        "education": profile.education or [],
        "projects": profile.projects or [],
    }


def _extract_resume_text(content: bytes, filename: str) -> str:
    """Extract text locally; no resume content is sent anywhere except the configured AI service."""
    suffix = Path(filename).suffix.lower()
    if suffix in {".txt", ".md", ".json"}:
        return content.decode("utf-8", errors="ignore").strip()
    if suffix == ".docx":
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as document:
                xml = document.read("word/document.xml")
            root = ElementTree.fromstring(xml)
            text = "\n".join(node.text for node in root.iter() if node.tag.endswith("}t") and node.text)
            return text.strip()
        except (KeyError, ValueError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
            raise HTTPException(status_code=400, detail="Unable to read this DOCX resume.") from exc
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail="Unable to extract text from this PDF. Upload a text-based PDF or DOCX file.",
            ) from exc
    raise HTTPException(status_code=400, detail="Unsupported resume format.")


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
    return _profile_response(profile)


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

        text_content = _extract_resume_text(content_bytes, filename)

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
    return _profile_response(updated)


@router.post("/analyze-and-queue", response_model=dict)
async def analyze_resume_and_queue_matches(
    queue_for_approval: bool = True,
    limit: int = 25,
    current_user: UserRecord = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
    job_repo: JobRepository = Depends(get_job_repo),
    match_repo: MatchRepository = Depends(get_match_repo),
    app_repo: ApplicationRepository = Depends(get_app_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    """Score saved jobs against the candidate's parsed resume.

    High-scoring jobs are placed in the candidate's approval queue only. This
    endpoint never submits an external application.
    """
    limit = max(1, min(limit, 100))
    profile = await profile_repo.get_or_create(current_user.id, current_user.full_name, str(current_user.email))
    skills = profile.skills or {}
    if not any(skills.get(key) for key in ("technical", "frameworks", "tools", "languages")):
        raise HTTPException(status_code=409, detail="Upload a resume with identifiable skills before searching for matches.")

    preferences = await profile_repo.get_preferences(current_user.id)
    jobs = await job_repo.list_jobs(limit=limit)
    candidate = {
        "headline": profile.headline,
        "summary": profile.summary,
        "skills": skills,
        "experience": profile.experience or [],
    }
    blacklist = {name.lower().strip() for name in (preferences.blacklisted_companies or [])}
    recommendations: List[Dict[str, Any]] = []
    queued_count = 0

    for job in jobs:
        if job.company_name.lower().strip() in blacklist:
            continue
        reasoning = await ai_service.evaluate_job_match(candidate, {
            "title": job.title,
            "companyName": job.company_name,
            "location": job.location,
            "workMode": job.work_mode,
            "descriptionText": job.description_text,
            "requirementsText": job.requirements_text or "",
        })
        score = max(0, min(100, int(reasoning.get("score", 0))))
        await match_repo.upsert(current_user.id, job.id, score, reasoning)
        queued = False
        if queue_for_approval and score >= preferences.min_match_score:
            # create() is idempotent for a user/job pair, so repeated analysis
            # cannot duplicate an application queue entry.
            existing = await app_repo.get_by_user_and_job(current_user.id, job.id)
            if existing is None:
                await app_repo.create(
                    user_id=current_user.id,
                    job_id=job.id,
                    status="QUEUED_FOR_APPROVAL",
                    notes="Resume match found; review materials before approving submission.",
                )
                queued_count += 1
                queued = True
        recommendations.append({
            "jobId": str(job.id), "companyName": job.company_name, "title": job.title,
            "externalUrl": job.external_url, "score": score, "reasoning": reasoning, "queued": queued,
        })

    recommendations.sort(key=lambda item: item["score"], reverse=True)
    await audit_repo.log(
        user_id=current_user.id,
        action="RESUME_ANALYZED_FOR_JOB_MATCHES",
        resource_type="profile",
        resource_id=str(profile.id),
        details={"jobs_scored": len(recommendations), "applications_queued": queued_count},
    )
    return {
        "profile": _profile_response(profile),
        "recommendations": recommendations,
        "queuedForApproval": queued_count,
        "message": "Jobs were scored from the uploaded resume. No application was submitted automatically.",
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
