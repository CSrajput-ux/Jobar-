# Database Audit

## Current schema

The checked-in schema defines users, OAuth tokens, profiles, resume variants, preferences, companies, jobs, matches, applications, application events, contacts, outreach campaigns, outreach emails, email threads, email messages, calendar events, suppression lists, audit logs, and usage limits.

## Schema gaps

- No migration framework or versioned migration files.
- The schema is applied directly during container initialization.
- No index plans are encoded in a portable migration.
- There is no role or tenant model.
- Resume versions and application documents are incomplete.
- Job sources and source health are not represented.
- Job embeddings and candidate embeddings are not tied to canonical update workflows.
- Notifications, automation runs, and AI usage are incomplete.
- User deletion and soft deletion are not defined.
- Application event history does not distinguish submission, approval, rejection, and failure events.
- Connection and integration status tables are absent.
- Data retention and deletion policies are not defined.

## Required migration strategy

- Use Alembic or an equivalent migration tool.
- Keep every schema change in a versioned migration.
- Test each migration from the latest production release against a disposable PostgreSQL database.
- Create HNSW indexes only when vector dimensions and model configuration are stable.
- Add indexes for the requested query paths.
- Use partial indexes for status and recent event queries where appropriate.

## Core data model

- Users: email, password hash, role, active status, verification, password reset, session, and timestamps.
- Profiles: canonical candidate facts, preference, resume source, and embedding.
- Resumes: master resume, versioned tailored documents, source job, and generated timestamp.
- Jobs: canonical source, external ID, company, normalized requirements, metadata, deduplication fingerprint, and timestamps.
- Matches: deterministic score components, AI reasoning, confidence, and generated content.
- Applications: one record per user/job attempt, document versions, status, timeline, and evidence.
- Recruiters: verified contact and relationship state.
- Emails and threads: Gmail IDs, direction, classification, status, and sent timestamps.
- Interviews: company, role, participants, date, URL, questions, notes, feedback.
- Notifications: type, read state, recurrence, and delivery state.
- Audit logs: actor, action, resource, metadata, IP, and timestamp.

## Integrity requirements

- Every user-owned foreign key must be constrained by the authenticated user.
- Unique constraints must prevent duplicate jobs, emails, calendar events, and applications in the intended business scope.
- Application status transitions must be validated.
- Job deduplication must use a stable canonical fingerprint.
- Soft deletion must preserve audit records while hiding records from normal queries.
- Database writes must be atomic when an application, event, and audit record must all be committed.

## Performance requirements

- Index jobs by company, posted date, location, work mode, source, and status.
- Index applications by user, status, and created date.
- Index matches by user and score.
- Index email threads by user and thread ID.
- Index interviews by date and user.
- Use cursor or offset pagination for large lists.
- Avoid N+1 queries and load only the fields needed by the current view.
