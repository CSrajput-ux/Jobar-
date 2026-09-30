import time
import logging
from typing import Dict, Type, List, Optional, Any
from app.ingestion.base import JobSource, SourceHealthStatus

logger = logging.getLogger("jobpilot.ingestion.registry")

class SourceRegistry:
    """
    Central Registry for all JobPilot ingestion sources.
    Enforces circuit-breaking, error rate tracking, and operational toggles.
    """
    _sources: Dict[str, Type[JobSource]] = {}
    _instances: Dict[str, JobSource] = {}
    _states: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, source_id: str):
        """Decorator to register a JobSource class."""
        def decorator(subclass: Type[JobSource]):
            cls._sources[source_id] = subclass
            cls._states[source_id] = {
                "id": source_id,
                "is_paused": False,
                "total_jobs_ingested": 0,
                "consecutive_failures": 0,
                "last_error": None,
                "last_synced_at": None,
                "circuit_open": False
            }
            logger.info(f"Registered JobSource connector: {source_id}")
            return subclass
        return decorator

    @classmethod
    def get_source(cls, source_id: str) -> Optional[JobSource]:
        if source_id not in cls._sources:
            return None
        if source_id not in cls._instances:
            cls._instances[source_id] = cls._sources[source_id]()
        return cls._instances[source_id]

    @classmethod
    def list_sources(cls) -> List[Dict[str, Any]]:
        results = []
        for s_id, subclass in cls._sources.items():
            instance = cls.get_source(s_id)
            meta = instance.meta if instance else None
            state = cls._states.get(s_id, {})
            results.append({
                "id": s_id,
                "name": meta.name if meta else s_id,
                "type": meta.source_type.value if meta else "unknown",
                "legal_status": meta.legal_status.value if meta else "unknown",
                "countries": meta.countries if meta else ["GLOBAL"],
                "rate_limit_per_min": meta.rate_limit_per_minute if meta else 60,
                "refresh_interval_hours": meta.refresh_interval_hours if meta else 6,
                "is_paused": state.get("is_paused", False),
                "circuit_open": state.get("circuit_open", False),
                "total_jobs": state.get("total_jobs_ingested", 0),
                "last_synced_at": state.get("last_synced_at"),
                "last_error": state.get("last_error")
            })
        return results

    @classmethod
    def toggle_pause(cls, source_id: str, paused: bool) -> bool:
        if source_id in cls._states:
            cls._states[source_id]["is_paused"] = paused
            logger.info(f"Source {source_id} pause status updated: {paused}")
            return True
        return False

    @classmethod
    def record_success(cls, source_id: str, new_jobs_count: int):
        if source_id in cls._states:
            state = cls._states[source_id]
            state["total_jobs_ingested"] += new_jobs_count
            state["consecutive_failures"] = 0
            state["last_error"] = None
            state["circuit_open"] = False
            state["last_synced_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    @classmethod
    def record_failure(cls, source_id: str, error_message: str):
        if source_id in cls._states:
            state = cls._states[source_id]
            state["consecutive_failures"] += 1
            state["last_error"] = error_message
            if state["consecutive_failures"] >= 5:
                state["circuit_open"] = True
                logger.warning(f"Circuit breaker tripped for source: {source_id}")

    @classmethod
    async def check_health(cls, source_id: str) -> SourceHealthStatus:
        instance = cls.get_source(source_id)
        if not instance:
            return SourceHealthStatus(is_healthy=False, status_code=404, latency_ms=0, error_message="Source not found")
        try:
            return await instance.health_check()
        except Exception as e:
            return SourceHealthStatus(is_healthy=False, status_code=500, latency_ms=0, error_message=str(e))

register_source = SourceRegistry.register
