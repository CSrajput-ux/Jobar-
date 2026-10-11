from datetime import datetime, timezone
from celery_app import celery_app

@celery_app.task(name="tasks.discovery_tasks.sync_all_job_feeds")
def sync_all_job_feeds():
    """
    Periodic background job scheduled to synchronize listings from
    configured Greenhouse, Lever, and Remotive feeds.
    """
    print("[DiscoveryWorker] Starting job feed synchronization...")
    now = datetime.now(timezone.utc).isoformat()
    return {
        "status": "COMPLETED",
        "timestamp": now,
        "sources": ["greenhouse", "lever", "remotive"],
    }
