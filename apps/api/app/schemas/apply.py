from typing import Optional, Dict, Any
from pydantic import BaseModel

class ApplicationCreate(BaseModel):
    jobId: str
    status: Optional[str] = "QUEUED_FOR_APPROVAL"
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    failureReason: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: str
    userId: str
    jobId: str
    status: str
    appliedAt: Optional[str] = None
    proofScreenshotUrl: Optional[str] = None
    submittedPayload: Optional[Dict[str, Any]] = None
    failureReason: Optional[str] = None
    notes: Optional[str] = None
    createdAt: str
    updatedAt: str
