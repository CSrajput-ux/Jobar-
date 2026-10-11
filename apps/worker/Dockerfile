# Production Dockerfile for JobPilot Background Celery Worker
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -u 1001 -m jobpilot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=jobpilot:jobpilot . /app

USER jobpilot
ENV PYTHONUNBUFFERED=1

CMD ["celery", "-A", "celery_app.celery_app", "worker", "--loglevel=INFO", "--concurrency=2"]
