from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import profile, jobs, matches, applications, outreach, inbox, calendar, audit
from app.ingestion import router as ingestion_router
from app.google import router as google_workspace_router

app = FastAPI(
    title="JobPilot Core API",
    description="Autonomous AI Job Search, Semantic Matching, Auto-Apply & Outreach Orchestration Engine",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for Next.js web application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(profile.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(matches.router, prefix=settings.API_V1_STR)
app.include_router(applications.router, prefix=settings.API_V1_STR)
app.include_router(outreach.router, prefix=settings.API_V1_STR)
app.include_router(inbox.router, prefix=settings.API_V1_STR)
app.include_router(calendar.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(ingestion_router.router, prefix=settings.API_V1_STR)

# Google Workspace Integration Routes (available at both root and /api/v1 for standard compatibility)
app.include_router(google_workspace_router.router)
app.include_router(google_workspace_router.router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "JobPilot API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
