from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    User,
    Profile,
    Preference,
    CommonQA,
    Job,
    JobMatch,
    Application,
    ApplicationEvent,
    Company,
    RecruiterContact,
    OutreachCampaign,
    OutreachEmail,
    EmailThread,
    CalendarEvent,
    AuditLog,
    SuppressionList,
)


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id: UUID, user_name: str = "", user_email: str = "") -> Profile:
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.execute(stmt)
        profile = result.scalar_one_or_none()
        if profile is None:
            profile = Profile(
                user_id=user_id,
                headline="Software Engineer",
                summary=f"Profile for {user_name or 'candidate'}.",
                location="Remote",
                skills={"technical": [], "frameworks": [], "tools": [], "languages": []},
                experience=[],
                education=[],
                projects=[],
            )
            self.session.add(profile)
            await self.session.flush()
            await self.session.refresh(profile)
        return profile

    async def update_profile(self, user_id: UUID, data: Dict[str, Any]) -> Profile:
        profile = await self.get_or_create(user_id)
        for key, value in data.items():
            if hasattr(profile, key) and key not in ("id", "user_id", "created_at"):
                setattr(profile, key, value)
        profile.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(profile)
        return profile

    async def get_preferences(self, user_id: UUID) -> Preference:
        stmt = select(Preference).where(Preference.user_id == user_id)
        result = await self.session.execute(stmt)
        prefs = result.scalar_one_or_none()
        if prefs is None:
            prefs = Preference(
                user_id=user_id,
                target_roles=["Software Engineer"],
                seniority_levels=["Mid", "Senior"],
                locations=["Remote"],
                work_modes=["remote"],
                min_salary_usd=120000,
                apply_mode="APPROVAL_QUEUE",
                daily_apply_cap=15,
                min_match_score=75,
            )
            self.session.add(prefs)
            await self.session.flush()
            await self.session.refresh(prefs)
        return prefs

    async def update_preferences(self, user_id: UUID, data: Dict[str, Any]) -> Preference:
        prefs = await self.get_preferences(user_id)
        for key, value in data.items():
            if hasattr(prefs, key) and key not in ("id", "user_id", "created_at"):
                setattr(prefs, key, value)
        prefs.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(prefs)
        return prefs

    async def get_common_qa(self, user_id: UUID) -> CommonQA:
        stmt = select(CommonQA).where(CommonQA.user_id == user_id)
        result = await self.session.execute(stmt)
        qa = result.scalar_one_or_none()
        if qa is None:
            qa = CommonQA(
                user_id=user_id,
                notice_period_days=14,
                work_auth_status="Authorized to work without sponsorship",
                requires_sponsorship=False,
                expected_salary_usd=150000,
                why_company_default="Excited by engineering culture and team mission.",
                custom_answers={},
            )
            self.session.add(qa)
            await self.session.flush()
            await self.session.refresh(qa)
        return qa

    async def update_common_qa(self, user_id: UUID, data: Dict[str, Any]) -> CommonQA:
        qa = await self.get_common_qa(user_id)
        for key, value in data.items():
            if hasattr(qa, key) and key not in ("id", "user_id", "created_at"):
                setattr(qa, key, value)
        qa.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(qa)
        return qa


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        work_mode: Optional[str] = None,
        ats_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Job]:
        stmt = select(Job)
        if query:
            q = f"%{query}%"
            stmt = stmt.where((Job.title.ilike(q)) | (Job.company_name.ilike(q)) | (Job.description_text.ilike(q)))
        if location:
            stmt = stmt.where(Job.location.ilike(f"%{location}%"))
        if work_mode:
            stmt = stmt.where(Job.work_mode.ilike(work_mode))
        if ats_type:
            stmt = stmt.where(Job.ats_type == ats_type)
        stmt = stmt.order_by(desc(Job.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, job_id: UUID) -> Optional[Job]:
        stmt = select(Job).where(Job.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, job_dict: Dict[str, Any]) -> Job:
        dedup_hash = job_dict.get("dedup_hash") or job_dict.get("dedupHash")
        stmt = select(Job).where(Job.dedup_hash == dedup_hash)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        job = Job(
            id=job_dict.get("id") if isinstance(job_dict.get("id"), UUID) else uuid4(),
            company_name=job_dict.get("company_name") or job_dict.get("companyName", "Company"),
            title=job_dict.get("title", "Role"),
            location=job_dict.get("location", "Remote"),
            work_mode=job_dict.get("work_mode") or job_dict.get("workMode", "remote"),
            description_text=job_dict.get("description_text") or job_dict.get("descriptionText", ""),
            requirements_text=job_dict.get("requirements_text") or job_dict.get("requirementsText"),
            salary_range=job_dict.get("salary_range") or job_dict.get("salaryRange"),
            source=job_dict.get("source", "connector"),
            external_url=job_dict.get("external_url") or job_dict.get("externalUrl", f"https://jobs.example.com/{uuid4()}"),
            dedup_hash=dedup_hash,
            ats_type=job_dict.get("ats_type") or job_dict.get("atsType"),
            posted_at=datetime.now(timezone.utc),
        )
        self.session.add(job)
        await self.session.flush()
        await self.session.refresh(job)
        return job


class MatchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: UUID, job_id: UUID) -> Optional[JobMatch]:
        stmt = select(JobMatch).where(JobMatch.user_id == user_id, JobMatch.job_id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        user_id: UUID,
        job_id: UUID,
        score: int,
        reasoning: Dict[str, Any],
        tailored_resume_json: Optional[Dict[str, Any]] = None,
        tailored_cover_letter: Optional[str] = None,
    ) -> JobMatch:
        match = await self.get(user_id, job_id)
        if match is None:
            match = JobMatch(
                user_id=user_id,
                job_id=job_id,
                score=score,
                reasoning=reasoning,
                tailored_resume_json=tailored_resume_json,
                tailored_cover_letter=tailored_cover_letter,
            )
            self.session.add(match)
        else:
            match.score = score
            match.reasoning = reasoning
            if tailored_resume_json:
                match.tailored_resume_json = tailored_resume_json
            if tailored_cover_letter:
                match.tailored_cover_letter = tailored_cover_letter
        await self.session.flush()
        await self.session.refresh(match)
        return match


class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(self, user_id: UUID, status: Optional[str] = None) -> List[Application]:
        stmt = select(Application).where(Application.user_id == user_id)
        if status:
            stmt = stmt.where(Application.status == status)
        stmt = stmt.order_by(desc(Application.created_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, user_id: UUID, app_id: UUID) -> Optional[Application]:
        stmt = select(Application).where(Application.user_id == user_id, Application.id == app_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: UUID,
        job_id: UUID,
        status: str = "SAVED",
        notes: Optional[str] = None,
    ) -> Application:
        stmt = select(Application).where(Application.user_id == user_id, Application.job_id == job_id)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        app = Application(
            user_id=user_id,
            job_id=job_id,
            status=status,
            notes=notes,
        )
        self.session.add(app)
        await self.session.flush()
        await self.session.refresh(app)

        # Log creation event
        event = ApplicationEvent(
            application_id=app.id,
            event_type="CREATED",
            metadata_json={"status": status, "notes": notes},
        )
        self.session.add(event)
        await self.session.flush()
        return app

    async def update_status(
        self,
        user_id: UUID,
        app_id: UUID,
        status: str,
        proof_url: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        failure_reason: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Application]:
        app = await self.get_by_id(user_id, app_id)
        if app is None:
            return None

        app.status = status
        if proof_url:
            app.proof_screenshot_url = proof_url
        if payload:
            app.submitted_payload = payload
        if failure_reason:
            app.failure_reason = failure_reason
        if notes:
            app.notes = notes
        if status == "APPLIED" and not app.applied_at:
            app.applied_at = datetime.now(timezone.utc)
        app.updated_at = datetime.now(timezone.utc)

        event = ApplicationEvent(
            application_id=app.id,
            event_type=f"STATUS_CHANGED_TO_{status}",
            metadata_json={"proof_url": proof_url, "failure_reason": failure_reason},
        )
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(app)
        return app


class OutreachRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_contacts(self) -> List[RecruiterContact]:
        stmt = select(RecruiterContact).order_by(RecruiterContact.company_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_or_create_contact(
        self,
        full_name: str,
        email: str,
        company_name: str,
        role_title: Optional[str] = None,
        linkedin_url: Optional[str] = None,
    ) -> RecruiterContact:
        stmt = select(RecruiterContact).where(RecruiterContact.email == email.lower())
        result = await self.session.execute(stmt)
        contact = result.scalar_one_or_none()
        if contact is None:
            contact = RecruiterContact(
                full_name=full_name,
                email=email.lower(),
                company_name=company_name,
                role_title=role_title,
                linkedin_url=linkedin_url,
                is_verified=True,
            )
            self.session.add(contact)
            await self.session.flush()
            await self.session.refresh(contact)
        return contact

    async def list_emails_by_user(self, user_id: UUID) -> List[OutreachEmail]:
        stmt = select(OutreachEmail).where(OutreachEmail.user_id == user_id).order_by(desc(OutreachEmail.created_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_email(
        self,
        user_id: UUID,
        campaign_id: UUID,
        contact_name: str,
        contact_email: str,
        company_name: str,
        subject: str,
        body_text: str,
        status: str = "PENDING_APPROVAL",
    ) -> OutreachEmail:
        email = OutreachEmail(
            user_id=user_id,
            campaign_id=campaign_id,
            sequence_step=0,
            contact_name=contact_name,
            contact_email=contact_email,
            company_name=company_name,
            subject=subject,
            body_text=body_text,
            status=status,
            scheduled_send_at=datetime.now(timezone.utc),
        )
        self.session.add(email)
        await self.session.flush()
        await self.session.refresh(email)
        return email

    async def get_email_by_id(self, user_id: UUID, email_id: UUID) -> Optional[OutreachEmail]:
        stmt = select(OutreachEmail).where(OutreachEmail.user_id == user_id, OutreachEmail.id == email_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_sent(self, user_id: UUID, email_id: UUID, message_id: Optional[str] = None) -> Optional[OutreachEmail]:
        email = await self.get_email_by_id(user_id, email_id)
        if email is None:
            return None
        email.status = "SENT"
        email.sent_at = datetime.now(timezone.utc)
        if message_id:
            email.gmail_message_id = message_id
        await self.session.flush()
        await self.session.refresh(email)
        return email


class InboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_threads_by_user(self, user_id: UUID) -> List[EmailThread]:
        stmt = select(EmailThread).where(EmailThread.user_id == user_id).order_by(desc(EmailThread.last_message_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_thread_by_id(self, user_id: UUID, thread_id: UUID) -> Optional[EmailThread]:
        stmt = select(EmailThread).where(EmailThread.user_id == user_id, EmailThread.id == thread_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_thread(
        self,
        user_id: UUID,
        gmail_thread_id: str,
        subject: str,
        from_address: str,
        snippet: str,
        classification: str,
        action_required: bool,
        proposed_reply: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> EmailThread:
        stmt = select(EmailThread).where(EmailThread.user_id == user_id, EmailThread.gmail_thread_id == gmail_thread_id)
        result = await self.session.execute(stmt)
        thread = result.scalar_one_or_none()
        if thread is None:
            thread = EmailThread(
                user_id=user_id,
                gmail_thread_id=gmail_thread_id,
                subject=subject,
                from_address=from_address,
                snippet=snippet,
                classification=classification,
                action_required=action_required,
                proposed_reply=proposed_reply,
                company_name=company_name,
                last_message_at=datetime.now(timezone.utc),
            )
            self.session.add(thread)
        else:
            thread.snippet = snippet
            thread.classification = classification
            thread.action_required = action_required
            if proposed_reply:
                thread.proposed_reply = proposed_reply
            thread.last_message_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(thread)
        return thread


class CalendarRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_events_by_user(self, user_id: UUID) -> List[CalendarEvent]:
        stmt = select(CalendarEvent).where(CalendarEvent.user_id == user_id).order_by(CalendarEvent.start_time)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_event(
        self,
        user_id: UUID,
        company_name: str,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        recruiter_email: Optional[str] = None,
        meet_link: Optional[str] = None,
        google_event_id: Optional[str] = None,
    ) -> CalendarEvent:
        event = CalendarEvent(
            user_id=user_id,
            company_name=company_name,
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            recruiter_email=recruiter_email,
            meet_link=meet_link,
            google_event_id=google_event_id or f"cal_{uuid4().hex[:12]}",
            status="confirmed",
        )
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        user_id: Optional[UUID],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
        )
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def list_logs_by_user(self, user_id: UUID, limit: int = 50) -> List[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.user_id == user_id).order_by(desc(AuditLog.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
