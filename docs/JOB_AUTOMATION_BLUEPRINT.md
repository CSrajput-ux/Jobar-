# Job application automation blueprint

This document maps the intended end-to-end job search workflow to the current
JobPilot codebase and separates working foundations from the integration work
still needed.

## Goal

Build a personal job-search assistant that can discover jobs, compare them with
the candidate's real profile, prepare application materials, help submit
applications on supported sites, monitor Gmail for job-related messages, and
keep an auditable application history.

Use explicit account authorization and truthful candidate information. Do not
bypass CAPTCHA, login walls, site restrictions, or other anti-automation
controls. Pause for the candidate whenever the site or application requires
manual work.

## End-to-end workflow

```text
Candidate profile + preferences
               |
               v
Discover jobs -> normalize + deduplicate -> match + score
                                          |
                                          v
                               shortlist / approval queue
                                          |
                         candidate reviews materials and answers
                                          |
                                          v
                               supported application flow
                                  |               |
                           submitted with      manual action
                           verified proof      required / error
                                  |               |
                                  +-------+-------+
                                          |
                                          v
                             application timeline + audit
                                          |
                                          v
Gmail OAuth -> incremental inbox sync -> job-email filter -> classify
                                          |
                              draft reply / interview alert
                                          |
                               candidate reviews and sends
```

## Existing code to build on

| Area | Existing foundation | Important gap |
|---|---|---|
| Candidate profile and preferences | `Profile`, `Preference`, and `CommonQA` in `apps/api/app/db/models.py` | Verify profile completeness and user-provided answers before queueing an application. |
| Job discovery and matching | Job/connectors, `Job`, `JobMatch`, discovery routes, and ingestion modules | `apps/worker/tasks/discovery_tasks.py` currently logs and returns a placeholder result; it does not persist discovered jobs. |
| Application pipeline | `Application`, `ApplicationEvent`, and routes in `apps/api/app/routers/applications.py` | The approve route currently marks an application `APPLIED` without submitting a real external application. Approval must not be treated as proof of submission. |
| Browser apply | `apps/worker/tasks/playwright_apply.py` | It fills some fields but does not click/verify a submit action or upload the resume. Its success path currently reports `APPLIED` after filling, so it must not be used as confirmed submission yet. |
| Google integration | OAuth, Gmail service, inbox routes, and `OAuthToken`/`EmailThread` models | The worker poll task is a placeholder. Persist sync cursors and message IDs, then connect the authorized Gmail API flow. |
| Background processing | Celery app schedules discovery hourly and inbox polling every 5 minutes | Scheduled tasks currently return placeholder results; production worker reliability and task state need implementation. |
| Deployment dependencies | Docker Compose includes API, worker, Redis, PostgreSQL, and MinIO | Configure real secrets and OAuth credentials outside source control before deployment. |

## Suggested state transitions

Keep approval separate from submission. Record each transition as an
`ApplicationEvent`.

```text
SAVED
  -> QUEUED_FOR_APPROVAL
  -> APPROVED
  -> SUBMITTING
  -> APPLIED                 only after verified submission evidence
  -> NEEDS_ATTENTION         CAPTCHA, login, unsupported form, or missing data
  -> FAILED                  retryable/non-retryable technical failure

APPLIED -> INTERVIEWING -> OFFERED
       \-> REJECTED
       \-> WITHDRAWN
```

The current status validator does not yet include every proposed state. Add
states through a migration and update API schemas, UI, worker behavior, and
tests together. Never set `APPLIED` merely because a user approved a job or a
form was filled.

## Data model plan

Reuse the current `User`, `Profile`, `Preference`, `CommonQA`, `Company`,
`Job`, `JobMatch`, `Application`, `ApplicationEvent`, `OAuthToken`, and
`EmailThread` models where possible.

Add or extend data only as needed:

- **Inbox sync state**: one row per user/provider with encrypted or otherwise
  protected history cursor, last successful sync time, and sync error state.
- **Email message deduplication**: store provider message ID and thread ID with
  a unique constraint per user; retain only job-related content needed by the
  product.
- **Application audit data**: record approval timestamp, submitted timestamp,
  submit evidence reference, worker attempt ID, and failure category in
  structured event metadata. Do not store access tokens or sensitive answers in
  event payloads.
- **Resume artifacts**: store a reference to the original and tailored file in
  private object storage; do not put file contents or public URLs in the
  application row.

Before adding tables, check migrations and existing repository methods for
equivalent structures.

## Background tasks

Implement these as idempotent Celery tasks. Each task should accept user/job or
application identifiers rather than credentials, check the user's kill switch
and authorization, and persist a clear success, retry, or manual-action result.

1. `sync_job_sources`: fetch from enabled sources, normalize, deduplicate, and
   persist jobs.
2. `score_new_jobs`: match jobs against a user's profile and preferences;
   avoid duplicate `JobMatch` rows.
3. `prepare_application`: create truthful tailored materials and identify
   unanswered questions; do not invent candidate experience or answers.
4. `submit_approved_application`: run only for explicitly approved
   applications and supported ATS flows; stop on CAPTCHA, login, unsupported
   forms, or site restrictions.
5. `sync_gmail_history`: fetch only the authorized account's incremental
   history, deduplicate messages, apply the job-related privacy filter, and
   update sync state.
6. `classify_job_email`: classify relevant messages and link them to an
   application only when there is sufficient evidence; otherwise ask the user.
7. `create_reply_draft`: create a Gmail draft for user review. Sending a reply
   should remain a separate, explicitly confirmed action.
8. `schedule_follow_up`: create a reminder or draft; require confirmation
   before sending unsolicited follow-up messages.

## API and UI surfaces

Build on the current application, inbox, profile, job, and preference routes.
The UI should provide:

- A profile readiness checklist and editable common application answers.
- Job match score, reasons, source, and application link.
- An approval queue showing the resume/cover letter version and any answers
  that will be used.
- Clear states for approved, in progress, submitted with evidence, and manual
  action required.
- A Gmail connection/revocation control and inbox sync status.
- Email classification with the original message context and a reviewable
  reply draft.
- A pause/kill switch and an audit timeline for automated actions.

## Implementation order

### Phase 1 — Correctness and honest status

- Change approval so it records approval only; it must not mark `APPLIED`.
- Make the worker submit task the only path that can record an automated
  submission, and require verified evidence before setting `APPLIED`.
- Add tests for transitions, ownership checks, duplicate jobs/applications,
  failures, and manual-action states.

### Phase 2 — Job discovery and shortlist

- Connect scheduled discovery to the existing connector/ingestion pipeline.
- Persist normalized jobs, deduplicate by stable source identifiers, and score
  against saved profiles/preferences.
- Show a useful shortlist and let users create approval-queue entries.

### Phase 3 — Gmail read and classify

- Use the existing Google OAuth/service architecture with least-privilege
  scopes and encrypted token storage.
- Implement incremental Gmail sync, durable cursor state, message
  deduplication, privacy filtering, and classification.
- Start with alerts and draft replies; do not silently send messages.

### Phase 4 — Supervised application submission

- Support one ATS flow at a time and test it against controlled fixtures.
- Validate required fields, upload the candidate-approved resume, and confirm
  the actual site's success response before recording `APPLIED`.
- Save private proof and an audit event. Stop for CAPTCHA, login, uncertain
  submission outcome, or unsupported questions.

### Phase 5 — Follow-up and production operations

- Add user-approved reminders/drafts, bounded retries, rate limits, monitoring,
  data retention controls, and a global pause switch.
- Test OAuth revocation, token refresh failures, worker restarts, and
  cross-user isolation before deployment.

## Release checklist

- A candidate explicitly connects Gmail and can disconnect it.
- Inbox polling reads only the authorized user's mailbox and does not process
  unrelated messages unnecessarily.
- No job application is submitted before user approval.
- No application is labeled `APPLIED` without verified evidence.
- CAPTCHA, login, ambiguous result, and unsupported form produce
  `NEEDS_ATTENTION`, never a false success.
- Retries cannot create duplicate applications, emails, or replies.
- All automated actions are user-scoped and auditable.
- OAuth secrets, encryption keys, and database credentials come from secure
  deployment configuration, not committed defaults.
