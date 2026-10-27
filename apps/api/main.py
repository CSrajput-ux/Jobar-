from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.database import get_engine
from app.db.models import Base
from app.routers import auth, profile, jobs, matches, applications, outreach, inbox, calendar, audit, platforms
from app.ingestion import router as ingestion_router
from app.google import router as google_workspace_router

logger = logging.getLogger("jobpilot.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup if in development/test
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized.")
    except Exception as exc:
        logger.warning(f"Database schema auto-init warning: {exc}")
    yield


app = FastAPI(
    title="JobPilot Core API",
    description="Autonomous AI Job Search, Semantic Matching, Auto-Apply & Outreach Orchestration Engine",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Request ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Global Standard Error Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        429: "RATE_LIMIT_EXCEEDED",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }
    return JSONResponse(
        status_code=exc.status_code,
        headers={"X-Request-ID": request_id, **(exc.headers or {})},
        content={
            "detail": exc.detail,  # Maintain backwards compatibility
            "error": {
                "code": code_map.get(exc.status_code, "ERROR"),
                "message": str(exc.detail),
                "details": [],
                "request_id": request_id,
            },
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        headers={"X-Request-ID": request_id},
        content={
            "detail": exc.errors(),
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters or payload.",
                "details": exc.errors(),
                "request_id": request_id,
            },
        },
    )


# CORS middleware for Next.js web application
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(profile.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(matches.router, prefix=settings.API_V1_STR)
app.include_router(applications.router, prefix=settings.API_V1_STR)
app.include_router(outreach.router, prefix=settings.API_V1_STR)
app.include_router(inbox.router, prefix=settings.API_V1_STR)
app.include_router(calendar.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(platforms.router, prefix=settings.API_V1_STR)
app.include_router(ingestion_router.router, prefix=settings.API_V1_STR)

# Google Workspace Integration Routes
app.include_router(google_workspace_router.router)
app.include_router(google_workspace_router.router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "JobPilot API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
