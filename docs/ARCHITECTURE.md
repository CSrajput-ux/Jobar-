# JobPilot System Architecture

## Architecture Overview
1. **Frontend**: Next.js 14 App Router with TailwindCSS.
2. **Core API**: FastAPI (Python 3.10+) serving REST endpoints for ingestion, applications, and calendar.
3. **Worker**: Celery distributed task runner with Redis broker and Playwright stealth runner.
4. **Google Workspace**: Incremental OAuth 2.0 PKCE, Gmail RFC 2822 threading, Sending Policy Engine, and Google Meet integration.
