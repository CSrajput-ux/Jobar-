from typing import Optional, List
from pydantic import BaseModel

class ContactResponse(BaseModel):
    id: str
    companyId: str
    companyName: str
    fullName: str
    email: str
    roleTitle: Optional[str] = None
    linkedinUrl: Optional[str] = None
    isVerified: bool

class OutreachEmailCreate(BaseModel):
    contactId: str
    jobId: str
    tone: Optional[str] = "confident_professional" # confident_professional, casual_warm, metrics_driven

class OutreachEmailResponse(BaseModel):
    id: str
    campaignId: str
    sequenceStep: int
    subject: str
    bodyText: str
    status: str
    scheduledSendAt: Optional[str] = None
    sentAt: Optional[str] = None

class EmailClassificationResponse(BaseModel):
    classification: str
    confidence: float
    detectedCompany: Optional[str] = None
    actionRequired: bool
    summarySnippet: str
    proposedReplyText: Optional[str] = None
