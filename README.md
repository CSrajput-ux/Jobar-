# 🚀 JobPilot

### AI-Powered Job Search, Matching, Application & Outreach Platform

**JobPilot** is an AI-assisted job search automation platform designed to turn the traditional job hunt into a structured, intelligent workflow.

Instead of manually searching hundreds of job boards, comparing job descriptions, tailoring resumes, tracking applications, checking recruiter emails, and coordinating interviews, JobPilot brings these workflows together into a single system.

> **Discover → Match → Tailor → Approve → Apply → Track → Engage**

---

## ✨ What is JobPilot?

Job hunting is fragmented across job boards, ATS platforms, email, calendars, spreadsheets, and personal notes.

JobPilot attempts to unify that workflow by combining:

- 🔎 Multi-source job discovery
- 🧠 AI-powered job-to-profile matching
- 📄 Job-specific resume tailoring
- ✉️ Personalized recruiter outreach
- 📬 Recruiter inbox intelligence
- 📅 Interview scheduling assistance
- ✅ Application pipeline management
- 🌐 Browser-based job clipping
- 🔐 Google Workspace integration
- ⚙️ Background workers for automation
- 🛡️ Sending policies, audit trails and safety controls

The goal is not simply to find jobs, but to build an **end-to-end job search operating system**.

---

# 🎯 Core Workflow

```text
                     ┌─────────────────────┐
                     │   Candidate Profile  │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │   Job Discovery     │
                     │ Greenhouse / Lever  │
                     │ Remotive / Others   │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │    AI Matching      │
                     │   Fit Score 0–100   │
                     └──────────┬──────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │ Resume & Cover Letter Tailor  │
                └──────────────┬────────────────┘
                               │
                               ▼
                     ┌─────────────────────┐
                     │ Application Queue   │
                     │ Save / Approve /    │
                     │ Apply / Track       │
                     └──────────┬──────────┘
                                │
                                ▼
                  ┌─────────────────────────┐
                  │ Recruiter Outreach      │
                  │ Cold Email / Follow-up  │
                  └────────────┬────────────┘
                               │
                               ▼
                     ┌─────────────────────┐
                     │ Gmail Intelligence  │
                     │ Classify / Reply     │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Interview Calendar  │
                     │ Scheduling / Meet   │
                     └─────────────────────┘
```

---

# 🌟 Key Features

## 🔎 Intelligent Job Discovery

JobPilot provides a connector-based ingestion architecture for discovering jobs from multiple sources.

Current connector architecture includes:

- Greenhouse
- Lever
- Ashby
- Adzuna
- Remotive
- Config-driven sources
- User-submitted company/career URLs
- ATS detection
- Company discovery

The ingestion pipeline includes normalization and deduplication so different sources can be converted into a consistent internal job representation.

### Example sources

```text
Greenhouse
Lever
Ashby
Remotive
Adzuna
Company Career Pages
Browser Extension
```

---

# 🧠 AI Job Matching

JobPilot evaluates a candidate profile against a job description and generates a structured match analysis.

The matching engine can produce:

```json
{
  "score": 93,
  "matchedSkills": [
    "PostgreSQL",
    "Python",
    "Redis"
  ],
  "missingSkills": [
    "Go"
  ],
  "redFlags": [],
  "fitSummary": "Strong alignment with the backend requirements.",
  "seniorityAlignment": "ideal"
}
```

### Matching signals include

- Technical skills
- Frameworks
- Tools
- Job description requirements
- Seniority
- Missing skills
- Potential red flags
- Overall fit score

The AI layer can also fall back to deterministic skill-overlap logic when an external AI model is unavailable.

---

# 📄 AI Resume Tailoring

JobPilot can generate job-specific resume variants while attempting to preserve the candidate's original experience.

The tailoring workflow is designed around a **zero-fabrication principle**:

> Optimize how existing experience is presented rather than inventing new experience.

The system can generate:

- Tailored experience bullets
- Skill-focused wording
- Job-specific summary
- Cover letter
- Original vs. tailored bullet differences

Example:

```text
Original:
Built FastAPI microservices.

Tailored:
Built high-throughput Python/FastAPI microservices.
```

This allows the candidate to understand exactly how their resume was adapted.

---

# ✅ Application Management

Applications can be organized into a structured pipeline.

Example statuses include:

```text
SAVED
QUEUED_FOR_APPROVAL
APPLIED
INTERVIEW
REJECTED
```

The frontend includes an application Kanban interface for managing this pipeline.

Each application can contain:

- Job information
- Application status
- Notes
- Applied timestamp
- Failure reason
- Submission metadata
- Proof/reference information

---

# ✉️ Recruiter Outreach

JobPilot includes an AI-powered outreach layer for creating personalized recruiter communication.

The system can generate different outreach styles such as:

- Professional
- Casual / warm
- Metrics-driven

Example workflow:

```text
Job Found
   ↓
Recruiter Identified
   ↓
AI Generates Personalized Email
   ↓
Policy Validation
   ↓
Draft / Approval
   ↓
Send
```

Outreach campaigns support sequencing concepts such as:

```text
Day 0
Day 3
Day 7
```

---

# 📬 Inbox Intelligence

JobPilot can classify incoming recruiter communication and identify actions that require attention.

Supported categories include:

- Interview invitations
- Assessments
- Recruiter questions
- Offers
- Rejections

Example:

```text
Incoming Email
      ↓
AI Classification
      ↓
Category + Confidence
      ↓
Action Required?
      ↓
Suggested Reply
```

Example output:

```json
{
  "classification": "INTERVIEW_INVITE",
  "confidence": 0.98,
  "actionRequired": true,
  "proposedReplyText": "Thank you for reaching out..."
}
```

---

# 📅 Interview & Calendar Automation

JobPilot includes calendar-oriented functionality for managing interview workflows.

The system is designed to support:

- Candidate availability
- Conflict-aware scheduling
- Interview event creation
- Google Meet links
- Recruiter email tracking
- Calendar integration

This turns recruiter communication into an actionable interview workflow rather than just an inbox notification.

---

# 🔐 Google Workspace Integration

One of the major components of JobPilot is its Google Workspace integration.

Supported architecture includes:

### Gmail

- OAuth authentication
- Gmail synchronization
- Thread retrieval
- Email classification
- Draft creation
- Email sending
- Reply handling

### Google Calendar

- Calendar event access
- Availability handling
- Interview scheduling
- Google Meet integration

### Security-oriented controls

The repository includes infrastructure for:

- OAuth state validation
- PKCE-based authentication
- Encrypted credential storage
- Sending policies
- Suppression lists
- Audit logging
- Kill switch
- Warm-up limits
- Quiet hours
- Human approval gates

---

# 🌐 1-Click Job Clipper

JobPilot also includes a Chromium-compatible browser extension.

The extension is designed to capture job listings directly from supported websites and send them into the JobPilot pipeline.

Currently configured website patterns include:

```text
LinkedIn
Indeed
Glassdoor
```

Architecture:

```text
Job Website
     │
     ▼
Chrome Extension
     │
     ▼
Job Extraction
     │
     ▼
JobPilot API
     │
     ▼
Matching / Tracking
```

---

# 🏗️ Architecture

JobPilot follows a modular application architecture.

```text
JobPilot
│
├── apps/
│   ├── api/
│   │   ├── FastAPI Backend
│   │   ├── AI Services
│   │   ├── Job Ingestion
│   │   ├── Google Integration
│   │   ├── Application APIs
│   │   └── Outreach APIs
│   │
│   ├── web/
│   │   ├── Next.js Frontend
│   │   ├── Dashboard
│   │   ├── Job Discovery
│   │   ├── Applications
│   │   ├── Inbox
│   │   ├── Outreach
│   │   ├── Calendar
│   │   └── Resume Tailoring
│   │
│   └── worker/
│       ├── Celery
│       ├── Discovery Tasks
│       ├── Email Tasks
│       └── Playwright Automation
│
├── packages/
│   ├── db/
│   │   ├── PostgreSQL Schema
│   │   ├── pgvector
│   │   └── Seed Data
│   │
│   └── shared/
│       ├── Types
│       └── Constants
│
├── extension/
│   └── Browser Job Clipper
│
├── docs/
│   ├── Architecture
│   └── Google Setup
│
└── docker/
    └── docker-compose.yml
```

---

# 🧩 Technology Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Backend

- Python
- FastAPI
- Pydantic
- Uvicorn
- HTTPX

## AI

- Anthropic API integration
- Deterministic fallback matching
- AI resume tailoring
- Email classification
- Outreach generation

## Database

- PostgreSQL
- pgvector
- JSONB
- UUID-based relational models
- HNSW vector indexes

## Background Processing

- Celery
- Redis

## Browser Automation

- Playwright
- Chromium Extension Manifest V3

## Integrations

- Gmail
- Google Calendar
- Greenhouse
- Lever
- Ashby
- Remotive
- Adzuna

## DevOps

- Docker Compose
- npm workspaces
- Pytest

---

# 🗄️ Database Design

JobPilot includes a relational PostgreSQL schema covering the major entities of the platform.

Core entities include:

```text
Users
Profiles
Preferences
Companies
Jobs
Job Matches
Resume Variants
Applications
Application Events
Contacts
Outreach Campaigns
Outreach Emails
Email Threads
Email Messages
Calendar Events
Suppression Lists
Audit Logs
Usage Limits
Google Accounts
OAuth Tokens
Gmail Sync State
Outbound Queue
```

Vector search support is provided through:

```sql
CREATE EXTENSION IF NOT EXISTS "vector";
```

and HNSW indexes are defined for vector similarity workloads.

---

# 🔒 Safety & Compliance-Oriented Design

Automation around email and job applications needs strong guardrails.

JobPilot therefore includes policy-oriented components for controlling automated actions.

### Email controls

```text
Warm-up limits
Daily send caps
Quiet hours
Suppression lists
Human approval
Draft-only mode
Auto-send mode
```

### Sensitive communications

Certain categories can require explicit human approval, including topics such as:

```text
Compensation
Offers
Legal matters
Visa / immigration
```

### Auditability

Important actions can be recorded with:

```text
Actor
Action
Target
Metadata
Timestamp
```

This makes automation more observable and controllable.

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/CSrajput-ux/Jobar-.git
cd Jobar-
```

---

## 2. Install Node.js dependencies

Node.js **18+** is required.

```bash
npm install
```

---

## 3. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Then configure the required API keys, database settings, Google OAuth credentials and other application secrets.

> Never commit your real `.env` file or production credentials.

---

# ▶️ Run the Web Application

```bash
npm run dev:web
```

The Next.js application will start in development mode.

---

# ▶️ Run the API

```bash
npm run dev:api
```

The backend is powered by FastAPI/Uvicorn.

---

# ▶️ Run Web + API Together

The repository uses `concurrently` for local development:

```bash
npm run dev
```

---

# 🧪 Testing

The repository contains backend and worker tests covering areas such as:

```text
AI service
API endpoints
Connectors
Global ingestion
Google Workspace
Security
Playwright application automation
```

Run:

```bash
npm test
```

---

# 🐳 Docker

A Docker Compose configuration is provided under:

```text
docker/docker-compose.yml
```

For a containerized development environment:

```bash
docker compose -f docker/docker-compose.yml up --build
```

---

# 🌍 Global Job Ingestion Architecture

JobPilot's ingestion system is designed around multiple discovery layers.

```text
                    Job Sources
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   Official APIs     ATS Feeds      Career Pages
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                 Source Registry
                        │
                        ▼
                   Normalizer
                        │
                        ▼
                  Deduplication
                        │
                        ▼
                 Job Repository
                        │
                        ▼
                  AI Matching
```

The repository includes connectors and source-management infrastructure intended to make additional job sources easier to add.

---

# 📁 Important Directories

| Directory | Purpose |
|---|---|
| `apps/api` | FastAPI backend |
| `apps/api/app/ingestion` | Job discovery and source ingestion |
| `apps/api/app/google` | Gmail / Calendar / OAuth integration |
| `apps/api/app/services` | AI and business services |
| `apps/web` | Next.js dashboard |
| `apps/worker` | Celery/background automation |
| `packages/db` | PostgreSQL database schema |
| `packages/shared` | Shared TypeScript types/constants |
| `extension` | Browser job clipping extension |
| `docs` | Architecture and setup documentation |
| `docker` | Docker Compose configuration |

---

# 🖥️ Dashboard Modules

The web application contains dedicated interfaces for:

```text
Overview
Job Discovery
Applications
Approval Queue
Inbox
Outreach
Resume Tailoring
Calendar
Google Integration
Sources / Administration
Settings
```

This provides a single workspace for the complete job-search lifecycle.

---

# 🔌 API Areas

The FastAPI backend exposes functional areas around:

```text
/jobs
/applications
/matches
/outreach
/inbox
/calendar
/profile
/sources
Google Workspace
Audit
```

This separation keeps discovery, matching, applications and communications modular.

---

# 🔮 Roadmap

Potential future improvements include:

- [ ] Persistent database-backed application state across all API flows
- [ ] More production-grade ATS connectors
- [ ] Additional job boards
- [ ] Advanced semantic/vector matching
- [ ] Better resume PDF generation
- [ ] Multi-profile / multi-resume support
- [ ] More robust browser automation
- [ ] Application failure recovery and retry workflows
- [ ] Advanced analytics and conversion tracking
- [ ] Interview preparation assistant
- [ ] Offer comparison and decision support
- [ ] Enterprise-grade observability
- [ ] Production deployment templates
- [ ] Expanded automated integration tests

---

# ⚠️ Project Status

**JobPilot is an active development project.**

The repository contains a substantial end-to-end architecture covering job discovery, AI matching, resume tailoring, applications, outreach, inbox intelligence, calendar workflows, browser extension support and Google Workspace integration.

However, some flows currently use mock/in-memory data or simulated responses in development-oriented backend paths. Production deployment therefore requires connecting these components to persistent infrastructure, real credentials, production data sources and appropriate operational safeguards.

---

# 🛡️ Security Notes

Before deploying JobPilot publicly:

1. Replace all development/mock credentials.
2. Configure strong secrets through environment variables.
3. Use a production PostgreSQL instance.
4. Configure Redis appropriately.
5. Configure Google OAuth credentials for the production domain.
6. Review email automation policies.
7. Verify application automation against target ATS platforms.
8. Enable HTTPS/TLS.
9. Protect internal/admin APIs.
10. Never commit API keys, OAuth credentials or tokens.

---

# 🤝 Contributing

Contributions are welcome.

A typical workflow:

```bash
git checkout -b feature/my-feature

# Make changes

npm test
npm run lint

git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

Then open a Pull Request.

---

# 📚 Documentation

Additional project documentation is available in:

```text
docs/ARCHITECTURE.md
docs/GOOGLE_SETUP_GUIDE.md
CHANGELOG.md
```

---

# 📄 License

Add the project's intended open-source license here before publishing the repository for external contributions.

---

# ⭐ Why JobPilot?

Traditional job searching often looks like:

```text
Search → Open Job → Read → Copy Details
→ Edit Resume → Apply → Send Email
→ Check Gmail → Track Spreadsheet
→ Schedule Interview
→ Repeat
```

JobPilot aims to transform that into:

```text
Profile
   ↓
Discover
   ↓
AI Match
   ↓
Tailor
   ↓
Approve
   ↓
Apply
   ↓
Outreach
   ↓
Inbox Intelligence
   ↓
Interview
   ↓
Track
```

### One platform. One pipeline. Smarter job search.

---

<p align="center">

**Built to make the job search less repetitive and more intelligent.**

⭐ Star the repository if you find the project interesting.

</p>
