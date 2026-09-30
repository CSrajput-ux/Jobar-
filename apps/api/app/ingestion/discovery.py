import re
import asyncio
from typing import List, Dict, Any, Optional
from app.ingestion.detector import ats_detector

class CompanyDiscoveryEngine:
    """
    Automated Company Registry & Expansion Loop.
    1. Seeds target companies from open datasets (Wikidata / Fortune 500 / YC directory).
    2. Probes domain careers paths & ATS subdomains.
    3. Auto-classifies ATS and links the appropriate connector.
    4. Supports high-priority user-submitted target companies.
    """

    def __init__(self):
        # In-memory company registry cache
        self._registry: Dict[str, Dict[str, Any]] = {
            "vercel.com": {
                "name": "Vercel",
                "domain": "vercel.com",
                "country": "US",
                "industry": "Developer Tools / Cloud",
                "ats_type": "greenhouse",
                "ats_slug": "vercel",
                "careers_url": "https://boards.greenhouse.io/vercel",
                "job_count": 28,
                "status": "active"
            },
            "linear.app": {
                "name": "Linear",
                "domain": "linear.app",
                "country": "US",
                "industry": "Issue Tracking / Productivity",
                "ats_type": "lever",
                "ats_slug": "linear",
                "careers_url": "https://jobs.lever.co/linear",
                "job_count": 14,
                "status": "active"
            },
            "supabase.com": {
                "name": "Supabase",
                "domain": "supabase.com",
                "country": "SG",
                "industry": "Open Source Database",
                "ats_type": "greenhouse",
                "ats_slug": "supabase",
                "careers_url": "https://boards.greenhouse.io/supabase",
                "job_count": 19,
                "status": "active"
            }
        }

    async def seed_from_wikidata(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Simulates / executes SPARQL query against Wikidata for technology enterprises
        with official websites, countries, and headquarters.
        """
        wikidata_seeds = [
            {"name": "HashiCorp", "domain": "hashicorp.com", "country": "US", "industry": "DevOps"},
            {"name": "Stripe", "domain": "stripe.com", "country": "US", "industry": "Fintech"},
            {"name": "Databricks", "domain": "databricks.com", "country": "US", "industry": "AI / Data"},
            {"name": "Canva", "domain": "canva.com", "country": "AU", "industry": "Design Software"},
            {"name": "GitLab", "domain": "gitlab.com", "country": "US", "industry": "Developer Tools"},
            {"name": "Postman", "domain": "postman.com", "country": "IN", "industry": "API Tooling"},
            {"name": "Miro", "domain": "miro.com", "country": "NL", "industry": "Visual Collaboration"},
            {"name": "Personio", "domain": "personio.com", "country": "DE", "industry": "HR Tech"}
        ]

        seeded_companies = []
        for seed in wikidata_seeds[:limit]:
            if seed["domain"] not in self._registry:
                # Discover ATS for seeded company
                detected = await ats_detector.detect_from_url(f"https://{seed['domain']}")
                profile = {
                    "name": seed["name"],
                    "domain": seed["domain"],
                    "country": seed["country"],
                    "industry": seed["industry"],
                    "ats_type": detected["atsType"],
                    "ats_slug": detected["companySlug"],
                    "careers_url": detected["careersUrl"],
                    "job_count": 0,
                    "status": "discovered"
                }
                self._registry[seed["domain"]] = profile
                seeded_companies.append(profile)

        return seeded_companies

    async def ingest_user_submitted_company(self, name_or_url: str) -> Dict[str, Any]:
        """
        User inputs e.g. 'ramp.com' or 'https://jobs.ashbyhq.com/ramp'.
        Enters the pipeline with immediate priority.
        """
        target = name_or_url.strip()
        if not target.startswith("http://") and not target.startswith("https://"):
            target = f"https://{target}"

        detected = await ats_detector.detect_from_url(target)
        slug = detected["companySlug"]
        domain = f"{slug}.com" if not target.startswith("https://jobs.") else target

        company_profile = {
            "name": slug.capitalize(),
            "domain": domain,
            "country": "GLOBAL",
            "industry": "Technology",
            "ats_type": detected["atsType"],
            "ats_slug": slug,
            "careers_url": detected["careersUrl"],
            "job_count": 5,
            "status": "active",
            "user_priority": True
        }

        self._registry[domain] = company_profile
        return company_profile

    def list_companies(self) -> List[Dict[str, Any]]:
        return list(self._registry.values())

company_discovery = CompanyDiscoveryEngine()
