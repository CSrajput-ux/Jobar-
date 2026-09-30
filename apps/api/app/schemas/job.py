from typing import Optional, List
from pydantic import BaseModel

class JobBase(BaseModel):
    companyName: str
    title: str
    location: str
    workMode: str
    descriptionText: str
    requirementsText: Optional[str] = None
    salaryRange: Optional[str] = None
    source: str
    externalUrl: str
    atsType: Optional[str] = None

class JobCreate(JobBase):
    dedupHash: str

class JobResponse(JobBase):
    id: str
    dedupHash: str
    postedAt: Optional[str] = None
    createdAt: str

class JobFilter(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    workMode: Optional[str] = None
    minScore: Optional[int] = None
    atsType: Optional[str] = None
    limit: int = 50
    offset: int = 0
