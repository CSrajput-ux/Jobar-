from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterator, List, Optional, Dict, Any

class SourceType(str, Enum):
    OFFICIAL_API = "api"
    ATS_CONNECTOR = "ats"
    STRUCTURED_DATA = "structured_data"
    CRAWLER = "crawler"
    PUBLIC_FEED = "feed"
    USER_SESSION = "extension"

class LegalStatus(str, Enum):
    OFFICIAL_API = "official_api"
    PUBLIC_FEED = "public_feed"
    ROBOTS_ALLOWED = "robots_allowed"
    USER_SESSION = "user_session"
    REQUIRES_REVIEW = "requires_review"

@dataclass
class SourceMeta:
    name: str
    source_type: SourceType
    legal_status: LegalStatus
    countries: List[str] = field(default_factory=lambda: ["GLOBAL"])
    rate_limit_per_minute: int = 60
    refresh_interval_hours: int = 6
    requires_api_key: bool = False
    description: str = ""

@dataclass
class RawJob:
    source_id: str
    external_id: str
    company_name: str
    title: str
    raw_payload: Dict[str, Any]
    external_url: str
    location: Optional[str] = None
    description: Optional[str] = None
    salary_raw: Optional[str] = None
    posted_at_raw: Optional[str] = None
    ats_type: Optional[str] = None

@dataclass
class NormalizedJob:
    id: str
    source: str
    company_name: str
    company_domain: Optional[str]
    title: str
    normalized_title: str
    seniority: str
    workplace_type: str # 'remote' | 'hybrid' | 'onsite'
    location_raw: str
    country: str
    city: Optional[str]
    salary_min_usd: Optional[int]
    salary_max_usd: Optional[int]
    currency: str
    skills: List[str]
    description_text: str
    apply_url: str
    apply_method: str # 'ats_api' | 'form' | 'email' | 'external'
    ats_type: Optional[str]
    dedup_hash: str
    posted_at: Optional[str]
    first_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    status: str = "active"

@dataclass
class SourceHealthStatus:
    is_healthy: bool
    status_code: int
    latency_ms: float
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

class JobSource(ABC):
    """
    Unified abstract interface for every JobPilot source:
    Layer 1 (Official APIs), Layer 2 (ATS Connectors), Layer 3 (JSON-LD),
    Layer 4 (AI Generic Extractor), and Layer 5 (Extension/Alerts).
    """
    meta: SourceMeta

    @abstractmethod
    async def discover(self) -> List[Dict[str, Any]]:
        """
        Discovers companies, boards, or target URLs indexed by this source.
        """
        pass

    @abstractmethod
    async def fetch_jobs(self, company_or_query: str) -> List[RawJob]:
        """
        Fetches raw job listings for a given company slug, board token, or search query.
        """
        pass

    @abstractmethod
    def parse(self, raw: RawJob) -> NormalizedJob:
        """
        Normalizes a RawJob into the unified schema.
        """
        pass

    @abstractmethod
    async def health_check(self) -> SourceHealthStatus:
        """
        Validates API connectivity, credentials, and endpoint latency.
        """
        pass
