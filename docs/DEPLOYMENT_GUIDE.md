# JobPilot Production Deployment Guide

This guide describes how to deploy JobPilot into production environments with zero downtime, high availability, and automated database migrations.

---

## 1. Quick Start (Production One-Liner)

### Linux / macOS:
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Windows (PowerShell):
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\deploy.ps1
```

---

## 2. Infrastructure Requirements

- **CPU**: 4+ Cores (recommended 8 cores for 50,000+ RPS)
- **RAM**: 8 GB minimum (16 GB recommended)
- **Disk**: 50 GB NVMe SSD
- **Docker**: Engine 24.0+ and Docker Compose v2.20+
- **Network**: Port 80 (HTTP) and 443 (HTTPS) open

---

## 3. Configuration & Secrets

1. Copy the production environment template:
   ```bash
   cp .env.production.example .env
   ```
2. Generate a secure 32-byte (64 hex characters) encryption master key:
   ```bash
   openssl rand -hex 32
   ```
3. Update `ENCRYPTION_MASTER_KEY`, `POSTGRES_PASSWORD`, and `MINIO_ROOT_PASSWORD` in `.env`.

---

## 4. Production Container Architecture

| Service | Image / Base | Internal Port | External Port | Role |
| :--- | :--- | :--- | :--- | :--- |
| **nginx** | `nginx:1.27-alpine` | 80, 443 | 80, 443 | High-concurrency edge reverse proxy & microcache |
| **api** | `python:3.10-slim` | 8000 | - | FastAPI high-throughput application server |
| **web** | `node:20-alpine` | 3000 | - | Next.js luxury SSR frontend |
| **worker** | `python:3.10-slim` | - | - | Celery distributed background job worker |
| **postgres** | `pgvector/pgvector:pg16` | 5432 | - | Relational storage with vector embeddings |
| **redis** | `redis:7.2-alpine` | 6379 | - | In-memory cache & task queue broker |
| **minio** | `minio/minio` | 9000, 9001 | - | S3-compatible resume and artifact storage |
| **migration** | `python:3.10-slim` | - | - | One-shot Alembic schema migration runner |

---

## 5. Health Checks & Monitoring

- **Liveness Probe**: `GET /health/live` (Returns HTTP 200 `{"status": "alive"}`)
- **Readiness Probe**: `GET /health/ready` (Verifies DB connection, returns HTTP 200 `{"status": "ready"}`)
- **System Telemetry**: `GET /metrics` (Returns cache state, RPS thresholds, and telemetry)

---

## 6. Backup & Recovery

### PostgreSQL Automated Backup:
```bash
docker exec -t jobpilot_prod_postgres pg_dump -U jobpilot jobpilot_prod_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### PostgreSQL Restore:
```bash
gunzip -c backup_YYYYMMDD_HHMMSS.sql.gz | docker exec -i jobpilot_prod_postgres psql -U jobpilot -d jobpilot_prod_db
```
