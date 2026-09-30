import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "jobpilot_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "tasks.discovery_tasks",
        "tasks.playwright_apply",
        "tasks.email_tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300, # 5 min max for browser jobs
    beat_schedule={
        "hourly-job-discovery": {
            "task": "tasks.discovery_tasks.sync_all_job_feeds",
            "schedule": 3600.0, # Every 60 minutes
        },
        "inbox-sync-polling": {
            "task": "tasks.email_tasks.poll_inbox_updates",
            "schedule": 300.0, # Every 5 minutes
        }
    }
)
