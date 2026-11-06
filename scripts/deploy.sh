#!/usr/bin/env bash
# ==============================================================================
# JobPilot Zero-Downtime Production Deployment Script
# ==============================================================================
set -euo pipefail

echo "=========================================================="
echo " Starting JobPilot Production Deployment"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$ROOT_DIR/docker"

cd "$ROOT_DIR"

# 1. Check for .env file
if [ ! -f "$DOCKER_DIR/.env" ] && [ ! -f "$ROOT_DIR/.env" ]; then
    echo "❌ Error: Production .env file not found!"
    echo "👉 Copy .env.production.example to .env and configure production credentials."
    exit 1
fi

echo "📦 1/5 Pulling latest dependencies and container base images..."
docker compose -f "$DOCKER_DIR/docker-compose.prod.yml" pull --ignore-buildable || true

echo "🔨 2/5 Building production microservice images..."
docker compose -f "$DOCKER_DIR/docker-compose.prod.yml" build --parallel

echo "💾 3/5 Starting persistence layers (PostgreSQL, Redis, MinIO)..."
docker compose -f "$DOCKER_DIR/docker-compose.prod.yml" up -d postgres redis minio

echo "⏳ Waiting for PostgreSQL healthy state..."
docker compose -f "$DOCKER_DIR/docker-compose.prod.yml" run --rm migration

echo "🚀 4/5 Launching API cluster, Worker, Next.js frontend, and Nginx Gateway..."
docker compose -f "$DOCKER_DIR/docker-compose.prod.yml" up -d --remove-orphans

echo "🩺 5/5 Performing health check validation..."
sleep 5
for i in {1..12}; do
    if curl -s -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ Deployment Successful! All systems are healthy and operational."
        echo "🌐 Public Gateway: http://localhost"
        echo "📊 Telemetry: http://localhost/metrics"
        exit 0
    fi
    echo "Waiting for health probe... ($i/12)"
    sleep 3
done

echo "⚠️ Health check timed out. Please review container logs with: docker compose -f docker/docker-compose.prod.yml logs"
exit 1
