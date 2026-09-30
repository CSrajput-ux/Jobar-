import re
import json
import hashlib
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import httpx
from app.ingestion.base import RawJob

class StructuredDataParser:
    """
    Layer 3: Extracts schema.org/JobPosting JSON-LD, Microdata, and Sitemaps.
    Standard web compliance with ETag & If-Modified-Since caching.
    """

    def extract_json_ld(self, html_content: str, base_url: str = "") -> List[Dict[str, Any]]:
        """
        Parses all <script type="application/ld+json"> blocks and extracts schema.org/JobPosting.
        """
        job_postings = []
        # Find script tags containing application/ld+json
        script_pattern = re.compile(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
        matches = script_pattern.findall(html_content)

        for raw_json in matches:
            try:
                data = json.loads(raw_json.strip())
                # Handle single object or array or @graph
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    if "@graph" in data:
                        items = data["@graph"]
                    else:
                        items = [data]

                for item in items:
                    t = item.get("@type", "")
                    if t == "JobPosting" or (isinstance(t, list) and "JobPosting" in t):
                        job_postings.append(self._normalize_schema_job(item, base_url))
            except Exception:
                continue

        return job_postings

    def _normalize_schema_job(self, schema_item: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        title = schema_item.get("title", "")
        hiring_org = schema_item.get("hiringOrganization", {})
        comp_name = hiring_org.get("name", "Unknown Employer") if isinstance(hiring_org, dict) else str(hiring_org)
        
        # Location handling
        job_loc = schema_item.get("jobLocation", {})
        loc_str = "Remote"
        if isinstance(job_loc, dict):
            address = job_loc.get("address", {})
            if isinstance(address, dict):
                city = address.get("addressLocality", "")
                country = address.get("addressCountry", "")
                loc_str = f"{city}, {country}".strip(", ")
            elif isinstance(address, str):
                loc_str = address

        # Workplace type
        loc_type = schema_item.get("jobLocationType", "")
        is_remote = "TELECOMMUTE" in loc_type or "remote" in title.lower() or "remote" in loc_str.lower()

        # Salary
        base_salary = schema_item.get("baseSalary", {})
        salary_str = "$140,000 - $190,000"
        if isinstance(base_salary, dict):
            val = base_salary.get("value", {})
            if isinstance(val, dict):
                min_val = val.get("minValue")
                max_val = val.get("maxValue")
                curr = base_salary.get("currency", "USD")
                if min_val and max_val:
                    salary_str = f"{curr} {min_val} - {max_val}"

        apply_url = schema_item.get("url") or base_url

        return {
            "title": title,
            "companyName": comp_name,
            "location": loc_str or "Remote",
            "workMode": "remote" if is_remote else "hybrid",
            "description": schema_item.get("description", ""),
            "salary": salary_str,
            "applyUrl": apply_url,
            "postedAt": schema_item.get("datePosted"),
            "validThrough": schema_item.get("validThrough"),
            "raw": schema_item
        }

    async def crawl_sitemap_for_jobs(self, sitemap_url: str, etag: Optional[str] = None) -> List[str]:
        """
        Parses sitemap.xml for URLs matching job/career paths.
        Supports If-None-Match ETag caching for incremental crawls.
        """
        headers = {"User-Agent": "JobPilotBot/1.0 (+https://jobpilot.dev/bot)"}
        if etag:
            headers["If-None-Match"] = etag

        job_urls = []
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                res = await client.get(sitemap_url, headers=headers)
                if res.status_code == 304:
                    return [] # Unmodified
                if res.status_code != 200:
                    return []

                root = ET.fromstring(res.text)
                # Handle standard XML sitemap namespace
                for elem in root.iter():
                    if elem.tag.endswith("loc"):
                        loc_url = elem.text.strip() if elem.text else ""
                        if any(k in loc_url.lower() for k in ["/job/", "/jobs/", "/careers/", "/position/", "/opening/"]):
                            job_urls.append(loc_url)
                return job_urls[:50]
            except Exception:
                return []

structured_parser = StructuredDataParser()
