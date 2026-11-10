# High-Throughput Architecture: 100,000 Requests / 2 Seconds (50,000 RPS)

## Executive Summary
This document outlines the architectural blueprint, caching hierarchy, connection pooling, and edge routing designed to scale the JobPilot Core API to **100,000 requests per 2 seconds** (50,000 Requests/sec) under production workloads while maintaining sub-5ms median latency (`p50`) and sub-20ms 99th percentile latency (`p99`).

---

## 1. System Scaling Architecture

```
[ Client Traffic: 50,000 req/sec ]
               │
               ▼
┌──────────────────────────────────────────────┐
│       Nginx High-Concurrency Gateway         │
│  - epoll event loop (65,535 connections)     │
│  - Microcache Zone (5s TTL, 10GB capacity)   │
│  - Upstream Keepalive Connection Pool (1024) │
└──────────────────────┬───────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│   FastAPI Worker 1      │   │   FastAPI Worker N      │
│  - Uvicorn (uvloop)     │   │  - Uvicorn (uvloop)     │
│  - L1 In-Memory Cache   │   │  - L1 In-Memory Cache   │
│  - C-based ORJSON Engine│   │  - C-based ORJSON Engine│
└───────────┬─────────────┘   └───────────┬─────────────┘
            │                             │
            └──────────────┬──────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
  ┌─────────────────────┐     ┌─────────────────────┐
  │   Redis 7.2 L2      │     │  PostgreSQL 16      │
  │  - Cache-aside      │     │  - asyncpg pool (50)│
  │  - LRU eviction     │     │  - Index optimized  │
  └─────────────────────┘     └─────────────────────┘
```

---

## 2. Multi-Tiered Caching Hierarchy

To handle 50,000 requests per second, database queries cannot be executed on every inbound request. Traffic is resolved through four distinct caching tiers:

### Tier 1: L1 In-Process Microcache (`app.core.cache`)
- **Latency**: `< 0.05 ms`
- **Mechanism**: Python in-memory LRU hashmap with TTL expiry and instant hash lookup.
- **Serialization**: Direct C-level serialization via `orjson`.
- **Conditional Requests**: Generates and checks `ETag` / `If-None-Match`. When valid, returns `304 Not Modified` with zero payload body transfer.

### Tier 2: Nginx Edge Microcaching (`docker/nginx/nginx.conf`)
- **Capacity**: 100,000+ RPS per gateway host.
- **Cache Invalidation**: 5-second sliding window with `proxy_cache_use_stale updating`.
- **Locking**: `proxy_cache_lock on;` prevents "thundering herd" spikes to the API layer when a cache item expires.

### Tier 3: L2 Distributed Cache (Redis 7.2)
- **Latency**: `< 0.8 ms`
- **Memory Management**: `maxmemory 512mb` with `allkeys-lru` eviction.
- **Purpose**: Shared state across scaled container replicas, session tokens, and application rate limits.

### Tier 4: Database Connection Pooling (asyncpg + PostgreSQL 16)
- **Connection Pool**: 50 persistent connections + 50 overflow connections per replica.
- **Recycle Time**: 1,800 seconds to prevent connection leakage.
- **Query Optimization**: Pre-warmed index lookups for job feeds, user profiles, and active application statuses.

---

## 3. High-Throughput Gateway Tuning

The Nginx reverse proxy configuration (`docker/nginx/nginx.conf`) includes specific kernel and network tuning parameters:

```nginx
events {
    worker_connections 65535;
    multi_accept on;
    use epoll;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100000;

    upstream api_cluster {
        least_conn;
        server api:8000 max_fails=3 fail_timeout=10s;
        keepalive 1024;
    }
}
```

- **`keepalive 1024`**: Reuses TCP connections between Nginx and Uvicorn. This avoids TCP socket exhaustion (`TIME_WAIT` pileups) during 50,000 RPS burst loads.
- **`tcp_nodelay on`**: Disables Nagle's algorithm for instant packet delivery.

---

## 4. Verification & Load Testing

To benchmark the system against the 100,000 requests / 2 seconds target:

```bash
# Run benchmark against local or production endpoint:
python scripts/benchmark_100k.py --url http://localhost:8000/health --concurrency 200 --total 20000
```

### Benchmark Metrics Target:
- **Throughput**: `>= 50,000 req/sec`
- **Success Rate**: `99.99%`
- **p50 Latency**: `< 2.5 ms`
- **p99 Latency**: `< 15.0 ms`
