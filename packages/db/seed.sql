-- ==============================================================================
-- JobPilot Seed Data Fixtures
-- ==============================================================================

-- 1. Default Test User
INSERT INTO users (id, email, full_name, is_active, kill_switch_active)
VALUES (
    'a0000000-0000-0000-0000-000000000001',
    'alex.chen.dev@gmail.com',
    'Alex Chen',
    TRUE,
    FALSE
) ON CONFLICT (id) DO NOTHING;

-- 2. Master Profile
INSERT INTO profiles (id, user_id, headline, summary, parsed_json)
VALUES (
    'b0000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'Staff Full-Stack & Distributed Systems Engineer',
    'Senior engineer with 8+ years building high-throughput cloud architectures, Python/FastAPI microservices, Next.js web applications, and resilient queue-driven automation.',
    '{
        "headline": "Staff Full-Stack & Distributed Systems Engineer",
        "location": "San Francisco, CA (Open to Remote)",
        "skills": {
            "technical": ["Python", "TypeScript", "Go", "PostgreSQL", "Redis", "Distributed Systems", "Kafka"],
            "frameworks": ["FastAPI", "Next.js", "React", "Node.js", "Celery", "Tailwind CSS"],
            "tools": ["Docker", "Kubernetes", "AWS", "Playwright", "Git", "Terraform", "CI/CD"],
            "languages": ["English (Native)", "Mandarin (Conversational)"]
        },
        "experience": [
            {
                "id": "exp-1",
                "company": "Veloce Cloud Systems",
                "title": "Staff Software Engineer",
                "startDate": "2021-03",
                "isCurrent": true,
                "location": "Remote",
                "highlights": [
                    "Architected event-driven microservices processing 45M daily events with 99.99% availability using FastAPI, Celery, and Redis.",
                    "Designed high-performance vector search engine using pgvector, reducing semantic lookup latency from 450ms to 42ms.",
                    "Mentored 6 engineers and spearheaded zero-downtime database schema migration workflows."
                ],
                "skillsUsed": ["Python", "FastAPI", "PostgreSQL", "pgvector", "Redis", "Docker"]
            },
            {
                "id": "exp-2",
                "company": "Aura AI Labs",
                "title": "Senior Full-Stack Engineer",
                "startDate": "2018-06",
                "endDate": "2021-02",
                "isCurrent": false,
                "location": "San Francisco, CA",
                "highlights": [
                    "Built real-time Next.js analytics platform with TanStack Query and WebSockets serving 120,000 MAU.",
                    "Implemented resilient browser automation agents with Playwright to extract structured insights from 200+ partner portals.",
                    "Optimized frontend bundle size by 44% and established enterprise design system with Tailwind CSS."
                ],
                "skillsUsed": ["Next.js", "TypeScript", "React", "Playwright", "Tailwind CSS"]
            }
        ],
        "education": [
            {
                "id": "edu-1",
                "institution": "University of California, Berkeley",
                "degree": "B.S. in Electrical Engineering & Computer Science",
                "fieldOfStudy": "Computer Science",
                "startDate": "2014-08",
                "endDate": "2018-05"
            }
        ],
        "projects": [
            {
                "id": "proj-1",
                "name": "HyperScale Queue Gateway",
                "description": "Open-source asynchronous task dispatcher with distributed deduplication and backpressure telemetry.",
                "url": "https://github.com/alexchen/hyperscale-queue",
                "technologies": ["Python", "Redis", "FastAPI"]
            }
        ]
    }'::JSONB
) ON CONFLICT (user_id) DO NOTHING;

-- 3. Preferences
INSERT INTO preferences (id, user_id, target_roles, seniority_levels, locations, work_modes, min_salary_usd, visa_sponsorship_required, apply_mode, daily_apply_cap, min_match_score)
VALUES (
    'c0000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    ARRAY['Staff Software Engineer', 'Senior Full Stack Engineer', 'Principal Backend Engineer']::TEXT[],
    ARRAY['Senior', 'Staff', 'Principal']::TEXT[],
    ARRAY['Remote', 'San Francisco, CA', 'New York, NY']::TEXT[],
    ARRAY['remote', 'hybrid']::TEXT[],
    175000,
    FALSE,
    'APPROVAL_QUEUE',
    15,
    75
) ON CONFLICT (user_id) DO NOTHING;

-- 4. Target Companies
INSERT INTO companies (id, name, domain, ats_type, ats_board_token, careers_url)
VALUES 
(
    'd0000000-0000-0000-0000-000000000001',
    'Linear',
    'linear.app',
    'lever',
    'linear',
    'https://jobs.lever.co/linear'
),
(
    'd0000000-0000-0000-0000-000000000002',
    'Vercel',
    'vercel.com',
    'greenhouse',
    'vercel',
    'https://boards.greenhouse.io/vercel'
),
(
    'd0000000-0000-0000-0000-000000000003',
    'Supabase',
    'supabase.com',
    'greenhouse',
    'supabase',
    'https://boards.greenhouse.io/supabase'
)
ON CONFLICT (id) DO NOTHING;

-- 5. Seed Real-world Jobs
INSERT INTO jobs (id, company_id, company_name, title, location, work_mode, description_text, requirements_text, salary_range, source, external_url, dedup_hash, ats_type)
VALUES
(
    'e0000000-0000-0000-0000-000000000001',
    'd0000000-0000-0000-0000-000000000001',
    'Linear',
    'Staff Infrastructure & Systems Engineer',
    'Remote (US / EU / Worldwide)',
    'remote',
    'Linear is looking for a Staff Systems Engineer to scale our distributed synchronization engine, real-time WebSocket protocol, and backend microservices.',
    '8+ years backend systems experience. Deep mastery of TypeScript/Node, distributed state synchronization, PostgreSQL, Redis, and high reliability architectures.',
    '$180,000 - $220,000 + Equity',
    'lever_api',
    'https://jobs.lever.co/linear/staff-infrastructure-systems',
    'hash_linear_staff_infra_2026',
    'lever'
),
(
    'e0000000-0000-0000-0000-000000000002',
    'd0000000-0000-0000-0000-000000000002',
    'Vercel',
    'Senior Full-Stack Engineer, AI Platforms',
    'Remote (United States)',
    'remote',
    'Join Vercel to shape the developer experience for modern AI web applications. You will build frontend interfaces with Next.js App Router and backend API orchestrators.',
    '5+ years with React, Next.js, TypeScript, modern CSS. Experience integrating LLM APIs, streaming responses, and optimizing web performance metrics.',
    '$170,000 - $210,000 + Equity',
    'greenhouse_api',
    'https://boards.greenhouse.io/vercel/jobs/5918239002',
    'hash_vercel_fullstack_ai_2026',
    'greenhouse'
),
(
    'e0000000-0000-0000-0000-000000000003',
    'd0000000-0000-0000-0000-000000000003',
    'Supabase',
    'Backend Engineer, Postgres & Vector Engine',
    'Remote',
    'remote',
    'Help scale Supabase pgvector and real-time database replication services for millions of developers worldwide.',
    'Deep expertise in PostgreSQL internals, pgvector, distributed storage, Go or Python, and multi-tenant security.',
    '$165,000 - $205,000 + Equity',
    'greenhouse_api',
    'https://boards.greenhouse.io/supabase/jobs/4829103002',
    'hash_supabase_postgres_vector_2026',
    'greenhouse'
)
ON CONFLICT (id) DO NOTHING;

-- 6. Match Scores
INSERT INTO job_matches (id, user_id, job_id, score, reasoning, tailored_cover_letter)
VALUES
(
    'f0000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'e0000000-0000-0000-0000-000000000002',
    96,
    '{
        "matchedSkills": ["Next.js", "TypeScript", "FastAPI", "React", "Tailwind CSS", "LLM APIs"],
        "missingSkills": [],
        "redFlags": [],
        "fitSummary": "Exceptional fit. Alex has 8+ years hands-on production Next.js and high-performance API experience directly matching Vercel AI platform priorities.",
        "seniorityAlignment": "ideal"
    }'::JSONB,
    'Dear Vercel Hiring Team, Having spent years scaling Next.js production web applications and integrating streaming LLM endpoints, I was thrilled to see your opening for Senior Full-Stack Engineer on AI Platforms...'
),
(
    'f0000000-0000-0000-0000-000000000002',
    'a0000000-0000-0000-0000-000000000001',
    'e0000000-0000-0000-0000-000000000003',
    93,
    '{
        "matchedSkills": ["PostgreSQL", "pgvector", "Python", "Distributed Systems", "Redis"],
        "missingSkills": ["Go Internals"],
        "redFlags": [],
        "fitSummary": "Outstanding backend alignment with direct pgvector production experience reducing query latency by 90%.",
        "seniorityAlignment": "ideal"
    }'::JSONB,
    'Dear Supabase Team, At Veloce Cloud Systems, I built vector search infrastructure using pgvector and PostgreSQL that powered 45M daily operations...'
)
ON CONFLICT (user_id, job_id) DO NOTHING;

-- 7. Applications in Pipeline
INSERT INTO applications (id, user_id, job_id, status, applied_at, notes)
VALUES
(
    '10000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'e0000000-0000-0000-0000-000000000002',
    'QUEUED_FOR_APPROVAL',
    NULL,
    'High match score (96%). Tailored resume and cover letter generated, ready for 1-click submission.'
),
(
    '10000000-0000-0000-0000-000000000002',
    'a0000000-0000-0000-0000-000000000001',
    'e0000000-0000-0000-0000-000000000003',
    'APPLIED',
    CURRENT_TIMESTAMP - INTERVAL '2 days',
    'Submitted via Greenhouse API automation. Screenshot proof verified.'
)
ON CONFLICT (user_id, job_id) DO NOTHING;

-- 8. Recruiter Contact & Outreach
INSERT INTO contacts (id, company_id, full_name, email, role_title, linkedin_url, is_verified)
VALUES (
    '20000000-0000-0000-0000-000000000001',
    'd0000000-0000-0000-0000-000000000002',
    'Sarah Jenkins',
    'sarah.j@vercel.com',
    'Senior Technical Recruiter (Engineering)',
    'https://linkedin.com/in/sarah-jenkins-tech',
    TRUE
) ON CONFLICT (company_id, email) DO NOTHING;

INSERT INTO outreach_campaigns (id, user_id, application_id, contact_id, status)
VALUES (
    '30000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000001',
    'DRAFT'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO outreach_emails (id, campaign_id, sequence_step, subject, body_text, status)
VALUES (
    '40000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    0,
    'Building AI web applications @ Vercel — Alex Chen',
    'Hi Sarah,

I noticed Vercel is scaling the AI Platforms team. Over the past 4 years, I have architected high-performance Next.js systems and distributed LLM pipelines, including an open-source queue gateway that handles 45M daily events.

I submitted an application for the Senior Full-Stack role and would welcome 10 minutes to connect if my background aligns with your roadmap.

Best regards,
Alex Chen | https://github.com/alexchen',
    'PENDING_APPROVAL'
) ON CONFLICT (id) DO NOTHING;

-- 9. Inbound Email Intelligence
INSERT INTO email_threads (id, user_id, application_id, gmail_thread_id, subject, from_address, snippet, classification, last_message_at)
VALUES (
    '50000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000002',
    'thread_supabase_recruiter_01',
    'Invitation to Interview: Backend Engineer @ Supabase',
    'careers@supabase.com',
    'Hi Alex, thanks for your application. The engineering team reviewed your background with pgvector and would love to schedule a 30-minute technical intro...',
    'INTERVIEW_INVITE',
    CURRENT_TIMESTAMP - INTERVAL '3 hours'
) ON CONFLICT (gmail_thread_id) DO NOTHING;
