# Jobar V2 Architecture

## Target architecture

The existing monorepo remains the preferred shape. The production architecture uses a thin Next.js frontend, a FastAPI application, PostgreSQL/pgvector, Redis/Celery, provider-neutral AI services, and user-owned integrations.

## Runtime boundaries

- Web: Next.js server and client components, authenticated browser requests, and typed API calls.
- API: FastAPI with dependency injection, authorization, validation, rate limits, request IDs, and standard error responses.
- Persistence: PostgreSQL with a repository layer and Alembic migrations.
- Worker: Celery tasks for discovery, extraction, AI processing, Gmail synchronization, and Playwright automation.
- AI: provider-neutral adapters with schema validation, fact validation, timeout, retry, and budget controls.
- Integrations: isolated Gmail and Calendar services with encrypted OAuth tokens and user ownership.
- Storage: object storage for documents and evidence; uploaded files are not stored in the database.

## Request flow

1. The browser sends an authenticated request with a request ID.
2. FastAPI validates the request and resolves the authenticated user.
3. Authorization checks the route policy and user ownership.
4. The repository reads or writes the owned record.
5. Services perform business logic and side-effect orchestration.
6. The database transaction commits the operation.
7. The API returns a standard response envelope.
8. The frontend updates state only from the persisted response.

## Ownership and authorization

Every user-owned record has an explicit owner ID. Global job-source and company records may be shared, but user-owned records are filtered by the authenticated user. Admin routes require the ADMIN role and must avoid returning private data unless necessary for support.

## Background task contract

Every task has a stable task ID, idempotency key, timeout, retry policy, logging context, and terminal state. Retryable failures use exponential backoff. The UI reports success only after the database confirms the operation.

## API layering

- Routers: request validation and route registration.
- Dependencies: authentication, authorization, request context, and rate limits.
- Schemas: request and response contracts.
- Services: business rules and orchestration.
- Repositories: database access and ownership filtering.
- Integrations: third-party clients and isolated credentials.

## Security boundaries

- CORS is restricted to configured origins.
- Session cookies are HTTP-only, Secure, and SameSite.
- Passwords use Argon2id or bcrypt.
- Refresh tokens rotate and are stored server-side.
- OAuth tokens are encrypted at rest and scoped to the authenticated user.
- Uploaded files are limited by MIME, extension, size, and content validation.
- Outbound URLs are checked against SSRF rules.

## Observability

Structured logs contain request ID, resource ID, task ID, duration, status, and error category. Logs redact tokens, passwords, credentials, and unnecessary email bodies.

## Deployment topology

- API and worker run separately and consume the same configuration.
- PostgreSQL and Redis are required before API readiness.
- AI-provider connectivity is a readiness dependency.
- The frontend is statically built and served through a managed host or Next.js server.
- Object storage holds resumes, documents, and automation evidence.
- Monitoring checks database, Redis, API, worker, and provider readiness.
