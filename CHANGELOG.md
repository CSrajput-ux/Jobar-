# JobPilot Changelog

All notable changes to the JobPilot platform and services are documented in this file.

## [v1.0.0] - 2026-11-12
### Added
- High-Throughput 100k requests / 2 seconds (50,000 RPS) gateway and L1 in-memory microcache.
- Nginx edge reverse proxy with epoll, 65,535 connections, and upstream keepalive connection pooling.
- Production multi-container Docker Compose cluster (`docker/docker-compose.prod.yml`).
- Automated zero-downtime deployment scripts (`scripts/deploy.sh` and `scripts/deploy.ps1`).
- GitHub Actions CI/CD pipeline covering backend tests, frontend builds, and Docker validation.
- Telemetry liveness and readiness probe endpoints (`/health/live`, `/health/ready`, `/metrics`).
- Dedicated async benchmark load-test harness (`scripts/benchmark_100k.py`).

## [v0.1.0] - 2026-09-25
### Initialized
- Initial multi-package monorepo topology (FastAPI backend, Next.js frontend, Celery workers).
- Global Job Coverage Layer with ATS connectors (Greenhouse, Lever, Ashby, Remotive).
- AES-256-GCM envelope encryption and security model.
- Autonomous Playwright application runner.
