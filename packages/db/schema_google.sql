-- ==============================================================================
-- JobPilot Google Workspace Schema Extension
-- ==============================================================================

-- 1. Connected Google Accounts (Supports multiple mailboxes per user)
CREATE TABLE IF NOT EXISTS google_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    google_sub VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    scopes TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    is_primary BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'ACTIVE', -- 'ACTIVE', 'NEEDS_RECONNECT', 'DISCONNECTED'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_google_sub UNIQUE(user_id, google_sub)
);

-- 2. Encrypted OAuth Tokens (AES-256-GCM)
CREATE TABLE IF NOT EXISTS oauth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES google_accounts(id) ON DELETE CASCADE,
    access_token_enc BYTEA NOT NULL,
    refresh_token_enc BYTEA,
    token_expiry TIMESTAMPTZ NOT NULL,
    key_id VARCHAR(50) DEFAULT 'kms-v1',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_account_oauth UNIQUE(account_id)
);

-- 3. Gmail Sync State & Watch Renewal
CREATE TABLE IF NOT EXISTS gmail_sync_state (
    account_id UUID PRIMARY KEY REFERENCES google_accounts(id) ON DELETE CASCADE,
    history_id VARCHAR(100),
    watch_expiry TIMESTAMPTZ,
    last_sync_at TIMESTAMPTZ,
    consecutive_failures INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Email Threads & Application Pipeline Link
CREATE TABLE IF NOT EXISTS email_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES google_accounts(id) ON DELETE CASCADE,
    gmail_thread_id VARCHAR(255) UNIQUE NOT NULL,
    application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
    subject VARCHAR(500),
    stage VARCHAR(50) DEFAULT 'RECEIVED', -- 'RECEIVED', 'INTERVIEW', 'REJECTED', 'OFFER'
    last_message_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Individual Email Messages & Categorization
CREATE TABLE IF NOT EXISTS email_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES email_threads(id) ON DELETE CASCADE,
    gmail_message_id VARCHAR(255) UNIQUE NOT NULL,
    direction VARCHAR(20) NOT NULL, -- 'INBOUND', 'OUTBOUND'
    from_address VARCHAR(255) NOT NULL,
    to_address VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    extracted_text TEXT,
    category VARCHAR(50), -- 'interview_invite', 'assessment_test', 'recruiter_question', 'rejection', 'offer'
    confidence FLOAT DEFAULT 0.0,
    sent_by_platform BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Outbound Sending Queue & Policy Enforcement
CREATE TABLE IF NOT EXISTS outbound_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES google_accounts(id) ON DELETE CASCADE,
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT NOT NULL,
    in_reply_to VARCHAR(255),
    references_header TEXT,
    gmail_thread_id VARCHAR(255),
    mode VARCHAR(50) DEFAULT 'DRAFT_ONLY', -- 'DRAFT_ONLY', 'APPROVE_THEN_SEND', 'AUTO_SEND'
    status VARCHAR(50) DEFAULT 'PENDING_APPROVAL', -- 'PENDING_APPROVAL', 'QUEUED', 'SENT', 'FAILED'
    scheduled_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMPTZ,
    attempts INT DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. Google Calendar Events & Slot Negotiations
CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES google_accounts(id) ON DELETE CASCADE,
    application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
    google_event_id VARCHAR(255) UNIQUE NOT NULL,
    ical_uid VARCHAR(255),
    summary VARCHAR(500) NOT NULL,
    start_utc TIMESTAMPTZ NOT NULL,
    end_utc TIMESTAMPTZ NOT NULL,
    meet_link TEXT,
    recruiter_email VARCHAR(255),
    status VARCHAR(50) DEFAULT 'CONFIRMED', -- 'TENTATIVE', 'CONFIRMED', 'CANCELLED'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 8. Suppression List & Audit Trails
CREATE TABLE IF NOT EXISTS suppression_list (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    reason VARCHAR(100) NOT NULL, -- 'UNSUBSCRIBED', 'BOUNCED', 'MANUAL_BLOCK'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_suppression_email UNIQUE(user_id, email)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    actor VARCHAR(50) NOT NULL, -- 'system', 'user', 'ai'
    action VARCHAR(100) NOT NULL, -- 'GMAIL_SYNC', 'DRAFT_CREATED', 'EMAIL_SENT', 'EVENT_CREATED', 'KILL_SWITCH'
    target VARCHAR(255),
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_expiry ON oauth_tokens(token_expiry);
CREATE INDEX IF NOT EXISTS idx_email_messages_thread ON email_messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_outbound_queue_status_sched ON outbound_queue(status, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_calendar_events_start ON calendar_events(account_id, start_utc);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_ts ON audit_logs(user_id, created_at DESC);
