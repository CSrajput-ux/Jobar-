# JobPilot 🚀
### Autonomous AI-Powered Job Search, Application & Outreach Platform

[![Next.js 14](https://img.shields.io/badge/Next.js-14%20App%20Router-black?style=flat&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.11-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-336791?style=flat&logo=postgresql)](https://github.com/pgvector/pgvector)
[![Claude 3.5](https://img.shields.io/badge/Claude%203.5-Sonnet-7C3AED?style=flat)](https://www.anthropic.com/)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth%20Automated-2EAD33?style=flat&logo=playwright)](https://playwright.dev/)

JobPilot is an enterprise-grade platform that automates the entire candidate search lifecycle: discovering global jobs across company career pages, tailoring resumes with a strict **Zero-Fabrication Guarantee**, applying via Playwright browser automation with screenshot proof, cold-emailing recruiters via authentic user Gmail API mailboxes, reading and classifying incoming recruiter replies, and scheduling interviews on Google Calendar.

---

## 🏗️ System Architecture

```
                          [ Chrome Extension (Manifest V3) ]
                                          │ (1-Click Clip)
                                          ▼
    [ Next.js 14 Web App ] <───> [ Next.js API Routes (BFF) ]
       (Tailwind / shadcn)                     │
                                               ▼
                                  [ FastAPI Core Backend ] ───> [ Claude 3.5 Sonnet ]
                                      │            │
                        ┌─────────────┘            └─────────────┐
                        ▼                                        ▼
            [ PostgreSQL 16 + pgvector ]                 [ Redis 7.2 Broker ]
            (Multi-tenant, AES-256 tokens)                       │
                                                                 ▼
                                                        [ Celery Worker Cluster ]
                                                        ├─ Ingestion (Greenhouse/Lever)
                                                        ├─ Playwright Stealth Runner
                                                        ├─ Gmail Sync & PubSub
                                                        └─ Hunter.io & GCal Dispatch
```

---

## 📦 Monorepo Directory Structure

```
jobpilot/
├── apps/
│   ├── web/               # Next.js 14 App Router, TypeScript, Tailwind, TanStack Query
│   ├── api/               # FastAPI backend: AI service, connectors, REST endpoints
│   ├── worker/            # Celery workers: Playwright form filler, feed discovery, email sync
│   └── extension/         # Chrome Extension (Manifest V3) for LinkedIn/Indeed 1-click clipping
├── packages/
│   ├── shared/            # Shared TypeScript contracts, types, enums, limits
│   └── db/                # Full PostgreSQL schema with pgvector, migrations, seed data
├── docker/
│   └── docker-compose.yml # PostgreSQL + pgvector, Redis 7.2, MinIO S3
├── .env.example           # Unified environment configuration
└── package.json           # Root workspaces orchestrator
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites
- **Node.js**: v18.0.0 or higher
- **Python**: 3.10 or 3.11
- **Docker**: Docker Desktop (for Postgres+pgvector, Redis, and MinIO)

### 2. Environment Setup
```bash
cp .env.example .env
```
Fill in your Google OAuth Client credentials (with Gmail + Calendar scopes enabled) and Anthropic API key.

### 3. Start Infrastructure Containers (Docker Compose)
```bash
docker compose -f docker/docker-compose.yml up -d
```
This boots:
- **PostgreSQL 16 + pgvector** on `localhost:5432` (auto-initializes schema + seed data)
- **Redis 7.2** on `localhost:6379`
- **MinIO S3 Console** on `http://localhost:9001` (login: `minioadmin` / `minioadmin`)

---

### 4. Start the Backend API (FastAPI)
```bash
cd apps/api
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```
API Documentation will be live at: `http://localhost:8000/docs`

---

### 5. Start Celery Background Workers & Playwright
```bash
cd apps/worker
# Activate the same virtual environment
pip install -r requirements.txt
playwright install chromium

# Start Celery Worker
celery -A celery_app worker --loglevel=info

# In a separate terminal, start Celery Beat for periodic hourly sync:
celery -A celery_app beat --loglevel=info
```

---

### 6. Start the Web Frontend (Next.js 14)
```bash
cd apps/web
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser to experience the JobPilot dashboard.

---

### 7. Install the Chrome Extension (1-Click Clipper)
1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Toggle on **"Developer mode"** in the top right.
3. Click **"Load unpacked"** and select the `/extension` directory.
4. Browse any job on LinkedIn or Indeed, click the JobPilot icon, and clip directly into your pipeline.

---

## 🛡️ Security, Privacy & AI Quality Guardrails

1. **Zero-Fabrication Guarantee:**  
   The AI operates as an editor, never an inventor. The post-generation AST schema validator rejects any bullet containing unlisted companies, metrics, or technologies not present in the candidate's master profile JSON.
2. **AES-256-GCM Token Encryption:**  
   OAuth tokens for Gmail and Google Calendar are encrypted at rest with unique 96-bit nonces. Decryption keys reside exclusively in isolated worker memory.
3. **Emergency Kill Switch:**  
   Engaging the kill switch (via UI header or `/api/v1/audit/kill-switch`) instantly freezes all active Celery workers, cancels pending browser sessions, and aborts outbound emails.
4. **Anti-Bot & Anti-Spam (CAN-SPAM / GDPR):**  
   - Playwright uses randomized human typing intervals (40–100ms jitter) and natural viewport dimensions.
   - **Never bypasses CAPTCHA.** When detected, the worker halts immediately, captures full screenshot proof, and alerts the candidate for 1-click completion.
   - Cold emails are sent from the candidate's authentic mailbox using an incremental warmup throttle (10 -> 20 -> 40/day max) with an instant opt-out footer.

---

## 🧪 Running the Test Suite

```bash
# Run Backend & AI Unit/Integration Tests
cd apps/api
pytest -v

# Run Playwright E2E Browser Automation Test
cd apps/worker
pytest -v tests/test_playwright_apply.py
```

---

## 🗺️ Roadmap
- [x] **MVP (Week 1–4):** Monorepo setup, Google OAuth2, CV parsing, Greenhouse/Lever/Remotive discovery, Claude Sonnet matching, Zero-fabrication resume tailoring, Playwright form-filler with approval queue, Cold outreach sequences, Inbound email intent classification, and Google Calendar scheduling.
- [ ] **V1:** Ashby & Workable ATS connectors, Chrome Web Store release, bidirectional Pub/Sub email webhooks.
- [ ] **V2:** Real-time AI voice interview simulator, live market compensation negotiation assistant, global visa-sponsor intelligence database.
