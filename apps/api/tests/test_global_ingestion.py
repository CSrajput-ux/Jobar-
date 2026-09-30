import pytest
from fastapi.testclient import TestClient
from main import app
from app.ingestion.registry import SourceRegistry
from app.ingestion.detector import ats_detector
from app.ingestion.structured_data import structured_parser
from app.ingestion.ai_extractor import ai_extractor
from app.ingestion.normalizer import job_normalizer
from app.ingestion.discovery import company_discovery

client = TestClient(app)

# 1. Source Registry & Dynamic Connectors
def test_source_registry_registration():
    sources = SourceRegistry.list_sources()
    source_ids = [s["id"] for s in sources]
    assert "greenhouse" in source_ids
    assert "lever" in source_ids
    assert "ashby" in source_ids
    assert "adzuna" in source_ids
    assert "remotive" in source_ids
    assert "himalayas" in source_ids # Config-driven JSON source

def test_source_registry_pause_toggle():
    # Pause source
    assert SourceRegistry.toggle_pause("ashby", True) is True
    sources = {s["id"]: s for s in SourceRegistry.list_sources()}
    assert sources["ashby"]["is_paused"] is True

    # Resume source
    assert SourceRegistry.toggle_pause("ashby", False) is True
    sources = {s["id"]: s for s in SourceRegistry.list_sources()}
    assert sources["ashby"]["is_paused"] is False

# 2. 5 Core Connectors & Config-Driven Source Contract
@pytest.mark.asyncio
async def test_greenhouse_connector_contract():
    source = SourceRegistry.get_source("greenhouse")
    assert source is not None
    raw_jobs = await source.fetch_jobs("vercel")
    assert len(raw_jobs) > 0
    parsed = source.parse(raw_jobs[0])
    assert parsed.source == "greenhouse"
    assert parsed.salary_min_usd > 100000
    assert len(parsed.dedup_hash) == 64

@pytest.mark.asyncio
async def test_lever_connector_contract():
    source = SourceRegistry.get_source("lever")
    assert source is not None
    raw_jobs = await source.fetch_jobs("linear")
    assert len(raw_jobs) > 0
    parsed = source.parse(raw_jobs[0])
    assert parsed.source == "lever"
    assert parsed.ats_type == "lever"

@pytest.mark.asyncio
async def test_ashby_connector_contract():
    source = SourceRegistry.get_source("ashby")
    assert source is not None
    raw_jobs = await source.fetch_jobs("ramp")
    assert len(raw_jobs) > 0
    parsed = source.parse(raw_jobs[0])
    assert parsed.source == "ashby"
    assert parsed.workplace_type in ["remote", "hybrid", "onsite"]

@pytest.mark.asyncio
async def test_adzuna_global_connector_contract():
    source = SourceRegistry.get_source("adzuna")
    assert source is not None
    raw_jobs = await source.fetch_jobs("python engineer")
    assert len(raw_jobs) > 0
    parsed = source.parse(raw_jobs[0])
    assert parsed.source == "adzuna"
    assert parsed.country == "US"

@pytest.mark.asyncio
async def test_remotive_feed_connector_contract():
    source = SourceRegistry.get_source("remotive")
    assert source is not None
    raw_jobs = await source.fetch_jobs("software-dev")
    assert len(raw_jobs) > 0
    parsed = source.parse(raw_jobs[0])
    assert parsed.workplace_type == "remote"

@pytest.mark.asyncio
async def test_declarative_config_driven_source():
    source = SourceRegistry.get_source("himalayas")
    assert source is not None
    assert source.meta.name == "Himalayas Remote Community Feed"
    raw_jobs = await source.fetch_jobs()
    assert len(raw_jobs) > 0
    parsed = source.parse(raw_jobs[0])
    assert parsed.source == "himalayas"

# 3. ATS Detector
@pytest.mark.asyncio
async def test_ats_detector_signatures():
    # Direct greenhouse link
    gh = await ats_detector.detect_from_url("https://boards.greenhouse.io/vercel")
    assert gh["atsType"] == "greenhouse"
    assert gh["companySlug"] == "vercel"

    # Lever link
    lever = await ats_detector.detect_from_url("https://jobs.lever.co/linear")
    assert lever["atsType"] == "lever"
    assert lever["companySlug"] == "linear"

    # Ashby link
    ashby = await ats_detector.detect_from_url("https://jobs.ashbyhq.com/retool")
    assert ashby["atsType"] == "ashby"
    assert ashby["companySlug"] == "retool"

    # Workday link
    wday = await ats_detector.detect_from_url("https://adobe.myworkdayjobs.com/en-US/external_careers")
    assert wday["atsType"] == "workday"
    assert wday["companySlug"] == "adobe"

# 4. Structured Data Parser (schema.org/JobPosting)
def test_json_ld_schema_org_extraction():
    html_sample = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org/",
          "@type": "JobPosting",
          "title": "Principal Distributed Systems Architect",
          "description": "Lead multi-region backend services at Scale.",
          "hiringOrganization": {
            "@type": "Organization",
            "name": "Acme Cloud"
          },
          "jobLocation": {
            "@type": "Place",
            "address": {
              "addressLocality": "San Francisco",
              "addressCountry": "US"
            }
          },
          "baseSalary": {
            "@type": "MonetaryAmount",
            "currency": "USD",
            "value": {
              "minValue": 180000,
              "maxValue": 240000
            }
          },
          "url": "https://acme.com/jobs/992"
        }
        </script>
      </head>
      <body><h1>Careers</h1></body>
    </html>
    """
    extracted = structured_parser.extract_json_ld(html_sample, "https://acme.com/jobs")
    assert len(extracted) == 1
    job = extracted[0]
    assert job["title"] == "Principal Distributed Systems Architect"
    assert job["companyName"] == "Acme Cloud"
    assert "San Francisco" in job["location"]
    assert "USD 180000 - 240000" in job["salary"]

# 5. AI Generic Extractor & Wrapper Caching
@pytest.mark.asyncio
async def test_ai_extractor_wrapper_caching():
    html_page = "<div><h3 class='role-title'>Senior Platform Engineer</h3><span class='location-tag'>Remote</span></div>"
    # First invocation uses or generates wrapper
    result = await ai_extractor.extract_from_page("customtech.io", html_page, "https://customtech.io/careers")
    assert len(result["jobs"]) > 0
    assert result["method"] == "cached_wrapper"
    assert result["cost_usd"] == 0.0 # Proves 0 LLM cost for cached wrapper!

# 6. Universal Job Normalizer
def test_universal_normalizer():
    title, seniority = job_normalizer.normalize_title("Staff Software Engineer - Infrastructure")
    assert title == "Staff Software Engineer"
    assert seniority == "Staff"

    min_usd, max_usd, curr = job_normalizer.normalize_salary("£80,000 - £110,000")
    assert curr == "GBP"
    assert min_usd == int(80000 * 1.28) # Converted to USD
    assert max_usd == int(110000 * 1.28)

    h1 = job_normalizer.compute_dedup_hash("Vercel", "Senior Full-Stack Engineer", "Remote")
    h2 = job_normalizer.compute_dedup_hash("vercel ", "senior full-stack engineer", " remote")
    assert h1 == h2 # Hash canonicalization

# 7. Ingestion API Endpoints
def test_ingestion_api_endpoints():
    # List sources
    res = client.get("/api/v1/sources")
    assert res.status_code == 200
    assert len(res.json()) >= 6

    # Test connector endpoint
    test_res = client.post("/api/v1/sources/greenhouse/test", json={"query": "vercel"})
    assert test_res.status_code == 200
    assert test_res.json()["status"] == "healthy"
    assert len(test_res.json()["sampleNormalized"]) > 0

    # ATS Detection endpoint
    detect_res = client.post("/api/v1/sources/detect-ats", json={"url": "https://boards.greenhouse.io/supabase"})
    assert detect_res.status_code == 200
    assert detect_res.json()["atsType"] == "greenhouse"

    # Coverage statistics
    coverage_res = client.get("/api/v1/sources/coverage")
    assert coverage_res.status_code == 200
    data = coverage_res.json()
    assert "globalMetrics" in data
    assert data["globalMetrics"]["countriesCovered"] >= 100
