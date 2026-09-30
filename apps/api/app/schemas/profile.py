from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ExperienceItemSchema(BaseModel):
    id: str
    company: str
    title: str
    startDate: str
    endDate: Optional[str] = None
    isCurrent: bool = False
    location: Optional[str] = None
    highlights: List[str] = []
    skillsUsed: List[str] = []

class EducationItemSchema(BaseModel):
    id: str
    institution: str
    degree: str
    fieldOfStudy: str
    startDate: str
    endDate: Optional[str] = None

class ProjectItemSchema(BaseModel):
    id: str
    name: str
    description: str
    role: Optional[str] = None
    url: Optional[str] = None
    technologies: List[str] = []

class StructuredProfileSchema(BaseModel):
    headline: str
    summary: str
    phone: Optional[str] = None
    location: str
    linkedinUrl: Optional[str] = None
    githubUrl: Optional[str] = None
    portfolioUrl: Optional[str] = None
    skills: Dict[str, List[str]] = Field(default_factory=lambda: {
        "technical": [],
        "frameworks": [],
        "tools": [],
        "languages": []
    })
    experience: List[ExperienceItemSchema] = []
    education: List[EducationItemSchema] = []
    projects: List[ProjectItemSchema] = []

class PreferencesSchema(BaseModel):
    targetRoles: List[str]
    seniorityLevels: List[str]
    locations: List[str]
    workModes: List[str]
    minSalaryUsd: Optional[int] = 120000
    visaSponsorshipRequired: bool = False
    blacklistedCompanies: List[str] = []
    targetIndustries: List[str] = []
    applyMode: str = "APPROVAL_QUEUE"
    dailyApplyCap: int = 15
    minMatchScore: int = 75

class CommonQASchema(BaseModel):
    noticePeriodDays: int = 14
    workAuthStatus: str = "Authorized to work in US without sponsorship"
    requiresSponsorship: bool = False
    expectedSalaryUsd: int = 150000
    whyCompanyDefault: str = "Excited by the mission and high-caliber engineering culture."
    customAnswers: Dict[str, Any] = {}
