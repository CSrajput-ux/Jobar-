-- ==============================================================================
-- JobPilot PostgreSQL Schema (with pgvector support)
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. USERS & SECURITY
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    kill_switch_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS oauth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'google'
    encrypted_access_token BYTEA NOT NULL, -- AES-256-GCM encrypted
    encrypted_refresh_token BYTEA,
    token_expiry TIMESTAMPTZ NOT NULL,
    scopes TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_provider UNIQUE(user_id, provider)
);

-- 2. CANDIDATE PROFILE & PREFERENCES
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    raw_cv_url TEXT,
    headline VARCHAR(255),
    summary TEXT,
    parsed_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resume_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL, -- e.g. "Full Stack Lead", "ML Infrastructure"
    target_role VARCHAR(150) NOT NULL,
    tailored_json JSONB NOT NULL,
    pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_roles TEXT[] NOT NULL DEFAULT ARRAY['Software Engineer']::TEXT[],
    seniority_levels TEXT[] NOT NULL DEFAULT ARRAY['Mid', 'Senior']::TEXT[],
    locations TEXT[] NOT NULL DEFAULT ARRAY['Remote', 'United States']::TEXT[],
    work_modes TEXT[] NOT NULL DEFAULT ARRAY['remote', 'hybrid']::TEXT[],
    min_salary_usd INT DEFAULT 120000,
    visa_sponsorship_required BOOLEAN DEFAULT FALSE,
    blacklisted_companies TEXT[] DEFAULT ARRAY[]::TEXT[],
    target_industries TEXT[] DEFAULT ARRAY[]::TEXT[],
    apply_mode VARCHAR(50) DEFAULT 'APPROVAL_QUEUE', -- 'MANUAL', 'APPROVAL_QUEUE', 'FULL_AUTO'
    daily_apply_cap INT DEFAULT 15,
    min_match_score INT DEFAULT 75,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS common_qa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notice_period_days INT DEFAULT 14,
    work_auth_status VARCHAR(100) DEFAULT 'Authorized to work in US without sponsorship',
    requires_sponsorship BOOLEAN DEFAULT FALSE,
    expected_salary_usd INT DEFAULT 150000,
    why_company_default TEXT DEFAULT 'Excited by the mission and high-caliber engineering culture.',
    custom_answers JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. COMPANIES & JOBS
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    ats_type VARCHAR(50), -- 'greenhouse', 'lever', 'ashby', 'workable', 'custom'
    ats_board_token VARCHAR(100),
    careers_url TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    company_name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL DEFAULT 'Remote',
    work_mode VARCHAR(50) NOT NULL DEFAULT 'remote',
    description_text TEXT NOT NULL,
    requirements_text TEXT,
    salary_range VARCHAR(100),
    source VARCHAR(50) NOT NULL, -- 'greenhouse_api', 'lever_api', 'remotive', 'extension'
    external_url TEXT UNIQUE NOT NULL,
    dedup_hash VARCHAR(64) UNIQUE NOT NULL,
    ats_type VARCHAR(50),
    embedding vector(1536),
    posted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. MATCHING & TAILORED CONTENT
CREATE TABLE IF NOT EXISTS job_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    score INT NOT NULL CHECK (score >= 0 AND score <= 100),
    reasoning JSONB NOT NULL,
    tailored_resume_json JSONB,
    tailored_cover_letter TEXT,
    tailored_pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_job_match UNIQUE(user_id, job_id)
);

-- 5. APPLICATIONS & EVENTS
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'SAVED',
    applied_at TIMESTAMPTZ,
    proof_screenshot_url TEXT,
    submitted_payload JSONB,
    failure_reason TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_job_application UNIQUE(user_id, job_id)
);

CREATE TABLE IF NOT EXISTS application_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. CONTACTS & OUTREACH
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role_title VARCHAR(255),
    linkedin_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_company_email UNIQUE(company_id, email)
);

CREATE TABLE IF NOT EXISTS outreach_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'DRAFT',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS outreach_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES outreach_campaigns(id) ON DELETE CASCADE,
    sequence_step INT NOT NULL, -- 0 (Day 0), 1 (Day 3), 2 (Day 7)
    subject VARCHAR(255) NOT NULL,
    body_text TEXT NOT NULL,
    gmail_message_id VARCHAR(255),
    gmail_thread_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'PENDING_APPROVAL',
    scheduled_send_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. INBOX INTELLIGENCE & CALENDAR
CREATE TABLE IF NOT EXISTS email_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
    gmail_thread_id VARCHAR(255) UNIQUE NOT NULL,
    subject VARCHAR(255),
    from_address VARCHAR(255) NOT NULL,
    snippet TEXT,
    classification VARCHAR(50),
    last_message_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS email_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES email_threads(id) ON DELETE CASCADE,
    gmail_message_id VARCHAR(255) UNIQUE NOT NULL,
    direction VARCHAR(20) NOT NULL, -- 'INBOUND', 'OUTBOUND'
    from_address VARCHAR(255) NOT NULL,
    to_address VARCHAR(255) NOT NULL,
    body_text TEXT NOT NULL,
    classification VARCHAR(50),
    is_draft BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
    google_event_id VARCHAR(255) UNIQUE NOT NULL,
    summary VARCHAR(255) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    meet_link TEXT,
    recruiter_email VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8. COMPLIANCE, AUDIT & USAGE LIMITS
CREATE TABLE IF NOT EXISTS suppression_list (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email_or_domain VARCHAR(255) NOT NULL,
    reason VARCHAR(100) NOT NULL, -- 'UNSUBSCRIBED', 'BOUNCED', 'USER_BLACKLIST'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_suppression UNIQUE(user_id, email_or_domain)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    details JSONB DEFAULT '{}'::JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usage_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    applications_submitted INT DEFAULT 0,
    outreach_emails_sent INT DEFAULT 0,
    ai_tokens_consumed INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_date_limits UNIQUE(user_id, date)
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_jobs_embedding ON jobs USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_profiles_embedding ON profiles USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_jobs_dedup_hash ON jobs(dedup_hash);
CREATE INDEX IF NOT EXISTS idx_jobs_source_posted ON jobs(source, posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_applications_user_status ON applications(user_id, status);
CREATE INDEX IF NOT EXISTS idx_email_threads_classification ON email_threads(user_id, classification);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
