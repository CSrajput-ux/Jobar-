import pytest
from app.services.connectors.greenhouse import greenhouse_connector
from app.services.connectors.lever import lever_connector
from app.services.connectors.remotive import remotive_connector

@pytest.mark.asyncio
async def test_greenhouse_connector():
    jobs = await greenhouse_connector.fetch_jobs("vercel")
    assert len(jobs) > 0
    first = jobs[0]
    assert "dedupHash" in first
    assert len(first["dedupHash"]) == 64 # SHA-256
    assert first["atsType"] == "greenhouse"

@pytest.mark.asyncio
async def test_lever_connector():
    jobs = await lever_connector.fetch_jobs("linear")
    assert len(jobs) > 0
    first = jobs[0]
    assert "dedupHash" in first
    assert first["atsType"] == "lever"

@pytest.mark.asyncio
async def test_remotive_connector():
    jobs = await remotive_connector.fetch_jobs("software-dev")
    assert len(jobs) > 0
    first = jobs[0]
    assert first["workMode"] == "remote"
