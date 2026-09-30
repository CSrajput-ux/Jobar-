from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.schemas.profile import ExperienceItemSchema

class MatchReasoningSchema(BaseModel):
    score: int
    matchedSkills: List[str]
    missingSkills: List[str]
    redFlags: List[str]
    fitSummary: str
    seniorityAlignment: str

class BulletDiffSchema(BaseModel):
    original: str
    tailored: str
    targetSkillHighlight: Optional[str] = None

class TailoredResumeSchema(BaseModel):
    targetRole: str
    companyName: str
    summary: str
    bulletDiffs: List[BulletDiffSchema]
    tailoredExperience: List[ExperienceItemSchema]
    matchingCoverLetter: str
    pdfUrl: Optional[str] = None

class JobMatchResponse(BaseModel):
    id: str
    userId: str
    jobId: str
    score: int
    reasoning: MatchReasoningSchema
    tailoredResume: Optional[TailoredResumeSchema] = None
    createdAt: str
