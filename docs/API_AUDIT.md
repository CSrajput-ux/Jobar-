# API Audit

## Current API surface

The backend exposes the following router groups: profile, jobs, matches, applications, outreach, inbox, calendar, audit, ingestion, and Google Workspace.

## Contract gaps

- Responses are not consistently wrapped as `{ data, meta }`.
- Errors do not use a stable machine-readable code and may expose internal messages.
- There is no authentication dependency on any route.
- There is no admin role check for audit, source, or system operations.
- The API does not define a user context or tenant boundary.
- Request IDs are not propagated into logs or responses.
- Pagination and filtering contracts are missing.
- Async operations do not return task IDs and failure states.
- External API errors are not normalized and may leak provider details.

## Required endpoint conventions

- `GET /api/v1/profile`: authenticated current user profile.
- `PUT /api/v1/profile`: update owned profile.
- `POST /api/v1/resumes`: upload and parse a resume.
- `GET /api/v1/jobs`: paginated, filtered, sorted job list.
- `GET /api/v1/jobs/{id}`: authenticated job detail.
- `POST /api/v1/jobs/discover`: queued discovery operation.
- `POST /api/v1/matches/{job_id}`: deterministic and AI-assisted match.
- `POST /api/v1/resumes/{resume_id}/tailor`: generated tailored resume.
- `POST /api/v1/applications`: create owned application record.
- `PATCH /api/v1/applications/{id}`: update status and timeline event.
- `POST /api/v1/applications/{id}/submit`: user-approved submission.
- `POST /api/v1/outreach/{id}/send`: sends only after explicit approval.
- `POST /api/v1/inbox/{thread_id}/classify`: classification and recommendation.
- `POST /api/v1/interviews/{id}/questions`: interview preparation.
- `POST /api/v1/calendar/events`: create calendar event.
- `GET /api/v1/analytics`: dashboard metrics.

## Error contract

Every API error must return:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": [],
    "request_id": "uuid"
  }
}
```

The backend must not return stack traces or provider secrets in production.

## Required status codes

- 200: successful read or completed request.
- 201: created resource.
- 202: asynchronous operation accepted.
- 400: invalid request.
- 401: missing or invalid authentication.
- 403: authenticated but unauthorized.
- 404: owned resource not found.
- 409: conflicting state.
- 429: rate limit exceeded.
- 502: upstream integration failure.
- 503: dependency unavailable.
