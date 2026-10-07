# Jobar V2 Repository Audit

## Scope and methodology

This audit was performed from the checked-in repository state on 2026-10-07. It reviewed the monorepo configuration, FastAPI routes, frontend components, database schema, worker code, integrations, tests, deployment assets, and documentation. No production data or external services were queried.

## Current architecture

- Frontend: Next.js 14 App Router, React 18, TypeScript, Tailwind CSS, TanStack Query, Lucide.
- Backend: FastAPI with Pydantic v2 and Pydantic Settings.
- Data: PostgreSQL 16 with pgvector in the documented deployment; the application currently has no SQLAlchemy ORM or migration framework.
- Background work: Celery and Redis are documented, but the worker package is not fully represented by the current workspace API package and requires separate verification.
- AI: Anthropic API integration through a service abstraction, with no provider-neutral interface or structured-output validation.
- Integrations: Google OAuth, Gmail, Calendar, job connectors, and Playwright.
- Extension: Manifest V3 Chrome extension with clipping and job-analysis interaction.

## Existing features

- Dashboard and navigation views for overview, discovery, applications, inbox, calendar, outreach, tailoring, settings, sources, and Google integration.
- FastAPI endpoints for profile, jobs, matching, applications, outreach, inbox, calendar, audit, ingestion, and Google Workspace.
- Greenhouse, Lever, Remotive, and Adzuna connectors.
- Resume parsing and AI matching service hooks.
- Playwright application workflow.
- Encrypted OAuth-token storage using AES-GCM.
- PostgreSQL schema with users, profiles, jobs, applications, contacts, outreach, inbox, calendar, audit, and usage tables.
- Docker Compose for PostgreSQL, Redis, and MinIO.

## Working features

- The API can start and expose a health endpoint.
- The backend test suite currently collects and passes 48 tests from the API package directory.
- The frontend contains a complete-looking dashboard and API client.
- The job connector modules contain source-specific parsing logic.
- The Google token encryption implementation uses a random nonce and authenticated encryption.
- The extension contains job clipping and analysis-related UI code.

## Broken features

1. The root test command is not reliable because the API is not an npm workspace package and the tests must be launched from the API directory.
2. The frontend build script uses Next.js 14 while the root package declares Node >=18; the current Try build must be verified after dependency installation.
3. The backend tests depend on process import state and do not use a shared test database.
4. The frontend API client does not consistently use the API response envelope and expects several endpoints that do not enforce the documented data contract.
5. The application has no authentication, authorization, user context, or protected route boundary.
6. The Google routes are not scoped to a user and can expose account-level operations.
7. Job and profile routes use process-global dictionaries and hardcoded candidate data.
8. Application approval is not persisted and does not use the existing application status model.
9. The JSON schemas do not reflect the full production records and can silently accept incomplete data.
10. The ingestion routes include global data mutations and a seed-companies operation that is unsafe for production.
11. The worker architecture is not migrated into a package with a testable task contract and no migration versioning.
12. The database schema is not executable as a migration baseline and contains unsafe defaults and missing required fields.

## Fake/mock features

- Hardcoded candidate profile, preferences, and common answers in the profile route.
- Hardcoded job catalog and match scores in the jobs route.
- Fake application records and approval behavior in the applications route.
- Fake Gmail and calendar behavior in Google integration tests and service modules.
- Fake success states in the frontend where API responses are not used.
- Development credentials and default encryption keys in configuration.
- Seed data in the database schema deployment path that is not isolated from production initialization.

## Security issues

- Default database credentials and encryption key are committed in configuration.
- CORS allows all origins with credentials.
- No CSRF, rate limiting, session expiration, password hashing, email verification, or password reset.
- No role-based authorization.
- No request IDs, access logging, or sensitive action audit.
- Google OAuth callbacks and Gmail operations lack a stable authenticated user identity.
- File upload handling is not present in the profile route; the current implementation reads arbitrary text and does not validate file type, size, or structure.
- External URLs and provider endpoints are not uniformly validated against SSRF restrictions.
- Error handling exposes raw exception details in several code paths.
- The API and worker lack consistent secrets validation and production environment checks.

## Performance issues

- In-memory global state is not scalable or thread-safe.
- No pagination, cursor, caching, query indexing, or database query optimization is demonstrated by the API routes.
- Job discovery and matching are not separated from the request path.
- More than one provider connector may be called synchronously for each sync request.
- Frontend components can render large lists without virtualization or bounded pagination.
- The Next.js application has no explicit code splitting or server/client boundary contract.

## Database issues

- No Alembic or equivalent migration framework is present.
- The schema is one monolithic file and is mounted directly into Docker initialization.
- The schema allows broad nullable values, lacks a user role model, and does not define deletion semantics consistently.
- Application uniqueness prevents one application per job, but the requested application lifecycle needs multiple attempts and event history.
- Job source metadata, resume versions, application documents, recruiter records, notifications, automation runs, and AI usage are absent or incomplete.
- The database has no foreign-key migration test and no test database fixture.
- The pgvector index setup is not covered by a migration test.

## AI issues

- The AI abstraction does not expose a provider-neutral common interface.
- Untrusted resume and job text is not wrapped in a strict prompt boundary.
- Structured output is not validated with Pydantic before use.
- No fact-validation or unsupported-claim guard is present.
- The profile and job routes can use AI without a user-scoped data source.
- AI latency, token limits, caching, retries, and provider routing are not controlled.

## UX issues

- The frontend displays data assumptions and status labels that are not tied to backend persistence.
- Loading, empty, error, retry, and authorization states are not consistently implemented.
- Accessibility, responsive behavior, and keyboard interactions need targeted verification.
- The API client uses any extensively and does not provide typed response envelopes.
- User actions are not consistently disabled while backend operations are pending.

## Production blockers

P0 authentication and user isolation.
P0 replace production mocks with database-backed records.
P0 migration framework and migration-tested database.
P0 production environment validation and secret handling.
P0 secure file upload and document validation.
P0 AI fact validation and structured output validation.
P0 database-backed application and email state.
P0 worker reliability and idempotency.
P0 frontend error and loading state cleanup.

## Recommended implementation order

1. Establish the test and development environment.
2. Add authentication, authorization, user ownership, and audit logging.
3. Introduce migrations and a test database.
4. Replace mock profile, jobs, applications, and outreach behavior with repository-backed services.
5. Add provider-neutral AI and fact validation.
6. Harden Google OAuth and Gmail/Calendar operations.
7. Finish worker reliability and idempotency.
8. Complete frontend integration and accessibility checks.
9. Add CI/CD and production deployment configuration.
