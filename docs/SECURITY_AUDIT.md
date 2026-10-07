# Security Audit

## Current security posture

The code has an AES-GCM token-encryption helper, but the overall application is not production secure. The demonstrated controls do not cover authentication, authorization, sessions, file uploads, request boundaries, or production secret management.

## Critical findings

- All production routes are currently unauthenticated.
- User data is global and not isolated by user.
- Default database and encryption secrets are present in source configuration.
- CORS permits all origins while credentials are enabled.
- No password hashing or account recovery is implemented.
- No email verification or session revocation is implemented.
- Google OAuth tokens and user account resources are not tied to a validated authenticated user.
- Ingestion routes mutate global source and company state.
- External URLs and file uploads are not safely bounded.
- AI prompts and personal data are not consistently treated as untrusted input.
- Audit logging does not cover sensitive actions.

## Required controls

- Argon2id password hashing with configurable cost.
- Email verification and password reset with single-use tokens.
- Secure HTTP-only session cookies with expiration and rotation.
- Refresh-token storage and revocation.
- Role checks on backend routes; never rely on frontend protection.
- Secret validation at startup with explicit development/test/production behavior.
- CORS allowlist and CSRF protection for cookie-authenticated endpoints.
- Rate limiting per user and IP.
- Input length, content type, MIME, file size, and archive integrity validation.
- SSRF-safe outbound URL validation.
- SQL parameterization through repositories.
- Audit logging with redaction and request IDs.
- Encryption at rest for OAuth tokens and sensitive PII.
- Explicit AI data retention and deletion settings.
- Human approval before sensitive email sends or application submissions.

## Anti-prompt-injection controls

- Treat resume, job description, email, and web content as untrusted data.
- Use structured delimiters and explicit system instructions.
- Never allow untrusted text to override output schema or business rules.
- Validate all model output before persistence.
- Maintain an explicit allowlist of candidate facts.
- Reject unsupported claims and return `needs_review` when evidence is missing.

## Data handling

- Do not log passwords, OAuth tokens, API keys, full email bodies, private resume content, or raw secrets.
- minimize PII in logs and audit metadata.
- encrypt sensitive tokens and apply retention policies.
- make deletion and export requests explicit and auditable.

## Production readiness gate

- Dependency audit and no-known-critical vulnerabilities.
- Security test suite for authentication, authorization, injection, upload, and rate limits.
- Secret scanning and CI configuration.
- Production configuration integrity tests.
- Manual review of all external API and browser automation paths.
