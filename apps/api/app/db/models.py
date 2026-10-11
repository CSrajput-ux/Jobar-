from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    Index,
    UUID as UUIDColumn,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[UserRole] = mapped_column(String(20), nullable=False, default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    kill_switch_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    sessions: Mapped[List[UserSession]] = relationship(back_populates="user", cascade="all, delete-orphan")
    profile: Mapped[Optional[Profile]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    preference: Mapped[Optional[Preference]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    common_qa: Mapped[Optional[CommonQA]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    applications: Mapped[List[Application]] = relationship(back_populates="user", cascade="all, delete-orphan")
    job_matches: Mapped[List[JobMatch]] = relationship(back_populates="user", cascade="all, delete-orphan")
    oauth_tokens: Mapped[List[OAuthToken]] = relationship(back_populates="user", cascade="all, delete-orphan")
    email_threads: Mapped[List[EmailThread]] = relationship(back_populates="user", cascade="all, delete-orphan")
    calendar_events: Mapped[List[CalendarEvent]] = relationship(back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[List[AuditLog]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="sessions")


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'google'
    encrypted_access_token: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    token_expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scopes: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    account_email: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="oauth_tokens")
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_user_provider"),)


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    headline: Mapped[str] = mapped_column(String(255), default="Software Engineer")
    summary: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[str] = mapped_column(String(255), default="Remote")
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text)
    github_url: Mapped[Optional[str]] = mapped_column(Text)
    skills: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    experience: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    education: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    projects: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    raw_cv_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="profile")


class Preference(Base):
    __tablename__ = "preferences"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    target_roles: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["Software Engineer"])
    seniority_levels: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["Mid", "Senior"])
    locations: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["Remote"])
    work_modes: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["remote"])
    min_salary_usd: Mapped[int] = mapped_column(Integer, default=120000)
    visa_sponsorship_required: Mapped[bool] = mapped_column(Boolean, default=False)
    blacklisted_companies: Mapped[List[str]] = mapped_column(JSON, default=list)
    target_industries: Mapped[List[str]] = mapped_column(JSON, default=list)
    apply_mode: Mapped[str] = mapped_column(String(50), default="APPROVAL_QUEUE")
    daily_apply_cap: Mapped[int] = mapped_column(Integer, default=15)
    min_match_score: Mapped[int] = mapped_column(Integer, default=75)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="preference")


class CommonQA(Base):
    __tablename__ = "common_qa"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    notice_period_days: Mapped[int] = mapped_column(Integer, default=14)
    work_auth_status: Mapped[str] = mapped_column(String(200), default="Authorized to work without sponsorship")
    requires_sponsorship: Mapped[bool] = mapped_column(Boolean, default=False)
    expected_salary_usd: Mapped[int] = mapped_column(Integer, default=150000)
    why_company_default: Mapped[str] = mapped_column(Text, default="Excited by engineering culture and team mission.")
    custom_answers: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="common_qa")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    ats_type: Mapped[Optional[str]] = mapped_column(String(50))
    ats_board_token: Mapped[Optional[str]] = mapped_column(String(100))
    careers_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    jobs: Mapped[List[Job]] = relationship(back_populates="company")
    contacts: Mapped[List[RecruiterContact]] = relationship(back_populates="company")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[Optional[UUID]] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(255), default="Remote")
    work_mode: Mapped[str] = mapped_column(String(50), default="remote")
    description_text: Mapped[str] = mapped_column(Text, nullable=False)
    requirements_text: Mapped[Optional[str]] = mapped_column(Text)
    salary_range: Mapped[Optional[str]] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # greenhouse_api, lever_api, etc.
    external_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    dedup_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    ats_type: Mapped[Optional[str]] = mapped_column(String(50))
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    company: Mapped[Optional[Company]] = relationship(back_populates="jobs")
    matches: Mapped[List[JobMatch]] = relationship(back_populates="job", cascade="all, delete-orphan")
    applications: Mapped[List[Application]] = relationship(back_populates="job", cascade="all, delete-orphan")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    reasoning: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    tailored_resume_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    tailored_cover_letter: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="job_matches")
    job: Mapped[Job] = relationship(back_populates="matches")
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_user_job_match"),)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="SAVED", index=True)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    proof_screenshot_url: Mapped[Optional[str]] = mapped_column(Text)
    submitted_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="applications")
    job: Mapped[Job] = relationship(back_populates="applications")
    events: Mapped[List[ApplicationEvent]] = relationship(back_populates="application", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),)


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    application_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    application: Mapped[Application] = relationship(back_populates="events")


class RecruiterContact(Base):
    __tablename__ = "contacts"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[Optional[UUID]] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True, index=True
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role_title: Mapped[Optional[str]] = mapped_column(String(255))
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    company: Mapped[Optional[Company]] = relationship(back_populates="contacts")
    campaigns: Mapped[List[OutreachCampaign]] = relationship(back_populates="contact")


class OutreachCampaign(Base):
    __tablename__ = "outreach_campaigns"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id: Mapped[Optional[UUID]] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("applications.id", ondelete="SET NULL"), nullable=True
    )
    contact_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    contact: Mapped[RecruiterContact] = relationship(back_populates="campaigns")
    emails: Mapped[List[OutreachEmail]] = relationship(back_populates="campaign", cascade="all, delete-orphan")


class OutreachEmail(Base):
    __tablename__ = "outreach_emails"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("outreach_campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sequence_step: Mapped[int] = mapped_column(Integer, default=0)
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    gmail_message_id: Mapped[Optional[str]] = mapped_column(String(255))
    gmail_thread_id: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="PENDING_APPROVAL", index=True)
    scheduled_send_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    campaign: Mapped[OutreachCampaign] = relationship(back_populates="emails")


class EmailThread(Base):
    __tablename__ = "email_threads"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id: Mapped[Optional[UUID]] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("applications.id", ondelete="SET NULL"), nullable=True
    )
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    gmail_thread_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    subject: Mapped[Optional[str]] = mapped_column(String(255))
    from_address: Mapped[str] = mapped_column(String(255), nullable=False)
    snippet: Mapped[Optional[str]] = mapped_column(Text)
    classification: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    confidence: Mapped[float] = mapped_column(Integer, default=0)
    action_required: Mapped[bool] = mapped_column(Boolean, default=False)
    proposed_reply: Mapped[Optional[str]] = mapped_column(Text)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="email_threads")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    application_id: Mapped[Optional[UUID]] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("applications.id", ondelete="SET NULL"), nullable=True
    )
    google_event_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    meet_link: Mapped[Optional[str]] = mapped_column(Text)
    recruiter_email: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="calendar_events")


class SuppressionList(Base):
    __tablename__ = "suppression_list"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email_or_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(String(100), default="USER_SUPPRESSED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (UniqueConstraint("user_id", "email_or_domain", name="uq_user_suppression"),)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(UUIDColumn(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[Optional[UUID]] = mapped_column(
        UUIDColumn(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100))
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )

    user: Mapped[Optional[User]] = relationship(back_populates="audit_logs")
