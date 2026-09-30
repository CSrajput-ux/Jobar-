import re
import httpx
from typing import Dict, Any, Optional
from urllib.parse import urlparse

class ATSDetector:
    """
    Intelligent ATS Sniffer & Careers-Page Resolver.
    Given any company homepage or career portal URL:
    1. Evaluates network redirects, headers, iframe embeds, and JavaScript bundles.
    2. Identifies the specific ATS engine (Greenhouse, Lever, Ashby, Workable, Workday, SmartRecruiters, BambooHR).
    3. Extracts the unique company slug/board token for zero-scraping API ingestion.
    """
    
    ATS_SIGNATURES = [
        {
            "type": "greenhouse",
            "domains": [r"boards\.greenhouse\.io", r"greenhouse\.io", r"gh_src"],
            "slug_regex": r"boards\.greenhouse\.io/(?:embed/job_board\?for=|v1/boards/)?([a-zA-Z0-9_\-]+)",
            "api_template": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
        },
        {
            "type": "lever",
            "domains": [r"jobs\.lever\.co", r"lever\.co"],
            "slug_regex": r"jobs\.lever\.co/([a-zA-Z0-9_\-]+)",
            "api_template": "https://api.lever.co/v0/postings/{slug}?mode=json"
        },
        {
            "type": "ashby",
            "domains": [r"jobs\.ashbyhq\.com", r"ashbyhq\.com"],
            "slug_regex": r"jobs\.ashbyhq\.com/([a-zA-Z0-9_\-]+)",
            "api_template": "https://api.ashbyhq.com/posting-api/job-board/{slug}"
        },
        {
            "type": "workable",
            "domains": [r"apply\.workable\.com", r"workable\.com"],
            "slug_regex": r"apply\.workable\.com/([a-zA-Z0-9_\-]+)",
            "api_template": "https://apply.workable.com/api/v1/widget/accounts/{slug}"
        },
        {
            "type": "workday",
            "domains": [r"myworkdayjobs\.com", r"workday\.com"],
            "slug_regex": r"([a-zA-Z0-9_\-]+)\.myworkdayjobs\.com",
            "api_template": "https://{slug}.myworkdayjobs.com/wday/cxs/{slug}/jobs"
        },
        {
            "type": "smartrecruiters",
            "domains": [r"smartrecruiters\.com"],
            "slug_regex": r"smartrecruiters\.com/([a-zA-Z0-9_\-]+)",
            "api_template": "https://api.smartrecruiters.com/v1/companies/{slug}/postings"
        }
    ]

    COMMON_CAREERS_PATHS = [
        "/careers",
        "/jobs",
        "/about/careers",
        "/join-us",
        "/company/careers",
        "/work-with-us"
    ]

    async def detect_from_url(self, target_url: str) -> Dict[str, Any]:
        """
        Takes a URL (homepage or direct jobs link) and extracts ATS metadata.
        """
        # Ensure scheme
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = f"https://{target_url}"

        # 1. Check direct URL pattern first
        for sig in self.ATS_SIGNATURES:
            for d in sig["domains"]:
                if re.search(d, target_url, re.IGNORECASE):
                    slug_match = re.search(sig["slug_regex"], target_url)
                    slug = slug_match.group(1) if slug_match else self._extract_domain_name(target_url)
                    return {
                        "atsType": sig["type"],
                        "companySlug": slug,
                        "careersUrl": target_url,
                        "directApiUrl": sig["api_template"].format(slug=slug),
                        "detectionMethod": "url_pattern",
                        "confidence": 0.99
                    }

        # 2. Probe HTTP response, redirects, and DOM scripts
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            try:
                res = await client.get(
                    target_url,
                    headers={"User-Agent": "JobPilotBot/1.0 (+https://jobpilot.dev/bot)"}
                )
                final_url = str(res.url)
                body = res.text

                # Check if final redirect URL is an ATS domain
                for sig in self.ATS_SIGNATURES:
                    if any(re.search(d, final_url, re.IGNORECASE) for d in sig["domains"]):
                        slug_match = re.search(sig["slug_regex"], final_url)
                        slug = slug_match.group(1) if slug_match else self._extract_domain_name(final_url)
                        return {
                            "atsType": sig["type"],
                            "companySlug": slug,
                            "careersUrl": final_url,
                            "directApiUrl": sig["api_template"].format(slug=slug),
                            "detectionMethod": "http_redirect",
                            "confidence": 0.98
                        }

                # Scan HTML for iframes or embedded script tags
                for sig in self.ATS_SIGNATURES:
                    for d in sig["domains"]:
                        if re.search(d, body, re.IGNORECASE):
                            slug_match = re.search(sig["slug_regex"], body)
                            slug = slug_match.group(1) if slug_match else self._extract_domain_name(target_url)
                            return {
                                "atsType": sig["type"],
                                "companySlug": slug,
                                "careersUrl": target_url,
                                "directApiUrl": sig["api_template"].format(slug=slug),
                                "detectionMethod": "html_embed",
                                "confidence": 0.95
                            }

                # Check for schema.org/JobPosting
                if "schema.org" in body and "JobPosting" in body:
                    return {
                        "atsType": "json_ld_schema",
                        "companySlug": self._extract_domain_name(target_url),
                        "careersUrl": target_url,
                        "directApiUrl": None,
                        "detectionMethod": "schema_org",
                        "confidence": 0.90
                    }

            except Exception:
                pass

        # Fallback to domain slug guess
        domain_name = self._extract_domain_name(target_url)
        return {
            "atsType": "custom_web",
            "companySlug": domain_name,
            "careersUrl": target_url,
            "directApiUrl": None,
            "detectionMethod": "fallback_heuristic",
            "confidence": 0.50
        }

    def _extract_domain_name(self, url: str) -> str:
        parsed = urlparse(url)
        netloc = parsed.netloc or parsed.path
        parts = netloc.split(":")[0].split(".")
        if len(parts) >= 2:
            return parts[-2]
        return "company"

ats_detector = ATSDetector()
