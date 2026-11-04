# Thungatha Scout — Technical Approach

**Status:** Current v1 implementation baseline  
**Updated:** 3 November 2026

## 1. Product model

Scout is an unattended employer-sourced vacancy ingestion and publishing system supporting Thungatha. The administrator's main recurring action is adding an employer by pasting an official careers/ATS URL and confirming the employer/source identity. Once a source is verified and activated, Scout operates automatically.

Routine human approval of every vacancy is not part of the operating model. Human attention is reserved for exceptions and administrative control.

V1 supports Greenhouse and Workday. Initial geography is Cape Town. Scout is not a public job-search frontend and has no recruiter self-service.

## 2. Deployment architecture

| Component            | Technology                                                              | Hosting                          |
| -------------------- | ----------------------------------------------------------------------- | -------------------------------- |
| Admin UI             | React, TypeScript, Vite, Tailwind CSS v3                                | Hosting provider pending         |
| Backend              | FastAPI (Python); separately executable scheduled/background processing | Provider decision pending        |
| Operational database | PostgreSQL via Supabase                                                 | Dedicated Scout Supabase project |
| Public destination   | Existing Thungatha Supabase/PostgreSQL                                  | Existing Thungatha project       |

Do not share Scout's operational schema/database with Thungatha. Do not use MongoDB or Azure Table Storage in the v1 architecture. Hosting remains deferred until local implementation and workload verification are complete.

The backend owns business rules and all privileged database writes. The React client uses Supabase Auth and calls protected backend endpoints. V1 permits only the administrator's explicitly configured email address; public registration is disabled. The backend independently validates Supabase access tokens and checks the authenticated email against a server-side allowlist on every protected operation. Frontend route guards are not a security boundary. The browser may contain only the Supabase URL and publishable/anon key, never a service-role key. Keep the allowlisted email in environment configuration, not source code. Use separate credentials for Scout and Thungatha.

## 3. Data ownership

**Scout project owns:**

- Employers and verification evidence.
- Employer sources and adapter configuration.
- Retrieved vacancy observations and normalised vacancies.
- Meaningful vacancy versions and content hashes.
- Extraction runs, diagnostics and source health.
- Quality outcomes, exceptions, admin corrections and audit events.
- Publication attempts, idempotency keys and sync state.

**Thungatha project owns:**

- The clean employer/vacancy records needed by the public product.
- Public visibility and application-facing lifecycle.

Never copy raw ATS payloads, rejected records, unresolved records or full extraction history into Thungatha. Publish only the approved-by-policy, quality-gate-passing projection. Scout retains provenance and its own publication ledger.

## 4. Employer onboarding

1. Admin pastes an official careers/ATS URL.
2. Backend normalises and validates the URL and detects Greenhouse or Workday.
3. If detection is uncertain, admin can choose/override the supported platform.
4. Adapter inspects the source and returns metadata, identifiers, test outcome and sample vacancies.
5. Admin confirms employer identity, Cape Town evidence and the official source relationship; uncertain metadata requires manual confirmation.
6. Backend registers employer/source idempotently.
7. Source is activated only after required verification and a meaningful retrieval test.

One employer can have multiple sources. Adding another source must not create a duplicate employer. Employer-specific board tokens, Workday tenant/site values and evidence live in source configuration, not adapter code.

## 5. Adapter contract

A small adapter interface covers:

- URL recognition and parsing.
- Source configuration validation.
- Employer/board metadata inspection.
- Paginated vacancy retrieval.
- Individual job detail retrieval where required.

Adapters own HTTP transport, platform parsing and pagination. They do not own quality policy, duplicate decisions, exception resolution or publishing.

Explicit outcomes: success with results, success empty, not found, blocked, rate-limited, timeout/transient, malformed and partial/incomplete.

### Greenhouse

Use the documented public Job Board API for a known board token:

- `GET /v1/boards/{board_token}`
- `GET /v1/boards/{board_token}/jobs?content=true`

This is board-specific, not a global customer directory. Validate response shape and pagination. Missing logo is not a blocker.

### Workday

Use observed public careers-site CXS JSON behavior, acknowledging it is undocumented and not guaranteed. Parse host, tenant and site separately. For `https://myhcm.wd3.myworkdayjobs.com/digioutsource`:

- host: `myhcm.wd3.myworkdayjobs.com`
- tenant: `myhcm`
- site: `digioutsource`

Common listing route: `https://{host}/wday/cxs/{tenant}/{site}/jobs`. Validate each tenant. Test DigiOutsource and at least one other tenant before claiming broad compatibility. HTTP 200 alone is not a successful source test.

## 6. Automated vacancy pipeline

```text
Scheduled/source-triggered retrieval
        |
        v
Persist source observation and run outcome
        |
        v
Normalize fields and content
        |
        v
Resolve source-scoped identity and duplicates
        |
        v
Apply deterministic quality gates
        |
        +---- Hard failure -> suppress/reject with reason
        |
        +---- Uncertainty -> exception queue
        |
        v
Qualifying vacancy
        |
        v
Idempotent publish to Thungatha
        |
        v
Record destination result and audit event
```

### Automatic publication gates

A vacancy is eligible only if:

1. Employer and source are active and verified.
2. Source relationship is official and use complies with applicable access restrictions/terms.
3. Stable source-scoped external identity exists.
4. Title, meaningful description, employer, credible location/remote arrangement and usable application destination are present.
5. Cape Town scope is supported; unknown is not assumed eligible.
6. It is not a confirmed or unresolved high-confidence duplicate.
7. Freshness and lifecycle checks pass.
8. Schema, URL and content validation pass.
9. The destination payload and stable idempotency key are valid.

Official ATS provenance is not enough by itself. Missing application URL, poor/incomplete content, ambiguous location, possible duplicates, malformed/suspicious content, uncertain source attribution and low-confidence classification are exceptions. Hard failures are suppressed with a reason; uncertainty is held for review.

AI may help extract or classify ambiguous content, but it cannot bypass hard gates, invent evidence or directly publish. Deterministic code owns URL validation, identity, deduplication, freshness, state transitions and publishing.

## 7. Versioning and lifecycle

- Match source-level vacancies by `(source_id, external_job_id)`.
- Normalise HTML/whitespace and hash meaningful fields with SHA-256.
- Unchanged records update last-seen metadata without creating a new version.
- Material changes create a version and are re-evaluated. If the change is uncertain or potentially harmful, hold the new version for exception review while preserving the last published version.
- Failed/partial extraction never implies vacancy removal or expiry.
- Only sufficiently complete successful inventories can support missing-vacancy reconciliation.
- Do not cross-employer deduplicate on title alone.
- Archive employers/sources and preserve audit/history; avoid destructive cascading deletes.

## 8. Exception management

The admin UI provides an Exceptions queue rather than a mandatory approval queue. It shows the reason, evidence, employer/source, extracted content, application link, prior version and suggested corrective action. Admin can correct permitted fields, reject/suppress, retry, or resolve the exception. Every action is audited.

Admin can also reject/unpublish a published vacancy, pause/resume a source, edit employer/source metadata, and archive records. These controls do not require routine intervention in successful runs.

## 9. Scheduling and resilience

Use a hosted scheduler/worker mechanism appropriate to the chosen backend host. Cadence is configurable and selected after measuring source count, runtime and provider limits. Prevent overlapping runs per source. Apply bounded timeouts, retries, exponential backoff and rate-limit handling. Record run completeness, counts, duration and sanitised diagnostics. A failed source must not mass-suppress or expire vacancies.

Publishing is idempotent and retryable. Keep a Scout-side publication ledger and reconcile destination state without copying operational history.

## 10. Storage discipline and cost

Scout stores structured operational records and meaningful versions. Do not retain full HTML/page snapshots by default. If raw evidence is required for a specific diagnostic/audit reason, retain it with a bounded policy and size limits. Avoid duplicate versions and unnecessary AI calls.

Supabase Free can support development/low-volume evaluation subject to current limits, inactivity pausing, backup and availability constraints. It is not automatically a production SLA. Decide on paid database/hosting before relying on uninterrupted production operation. The exhausted Azure for Students credit is not a basis for assuming Azure resources are free. No paid resource or subscription upgrade without explicit approval.

## 11. Security

- Private admin authentication and backend authorization.
- Separate Scout and Thungatha project credentials.
- No service-role key in browser bundles.
- Validate external/AI data at boundaries.
- Bound requests, payload sizes, retries, scheduled workloads and logs.
- Never bypass source access restrictions, quotas or terms.
- Redact secrets and unnecessary personal data from diagnostics.

## 12. Verification

Unit tests cover URL parsing, adapters, config validation, normalisation, hashing, duplicate handling, quality gates, state transitions and idempotency. Contract tests use recorded ATS fixtures. PostgreSQL integration tests cover schema constraints and persistence. Live smoke tests for Greenhouse and Workday are separately recorded.

Critical safety tests:

- Missing application URL cannot auto-publish.
- Uncertain location cannot silently pass Cape Town scope.
- Duplicate candidates are held/suppressed correctly.
- Failed/partial extraction cannot expire vacancies.
- Unchanged content does not create a new version.
- Unqualified or exception records never publish.
- Publishing retry does not duplicate destination records.
- Scout-only operational data never leaks into Thungatha.

## 13. Locked project setup — 3 November 2026

- Backend HTTP framework: **FastAPI**, with Pydantic settings and Uvicorn for local development. Scheduled/background processing remains separately executable and provider-portable.
- Frontend: **React + TypeScript + Vite + Tailwind CSS v3**.
- Admin authentication: **Supabase Auth**, restricted to one configured administrator email. Disable public sign-up/registration. Backend validates Supabase JWTs and enforces the email allowlist for every protected operation.
- Keep the admin email allowlist in server-side environment configuration. The browser receives only the Supabase URL and publishable/anon key; never expose a service-role key.
- Initial PostgreSQL persistence uses **Psycopg 3 with explicit SQL**, not an ORM. Versioned SQL files under `backend/database-migrations/` are applied by the small in-repository migration runner, which records SHA-256 checksums and serializes concurrent runs with a transaction-scoped advisory lock. Do not add SQLAlchemy/Alembic without a demonstrated need.
- Supabase Transaction Pooler connections use TLS, a bounded connection timeout and `prepare_threshold=None` to avoid session-level prepared-statement assumptions. The backend opens direct connections per operation; no connection-pool framework is introduced for the current low-volume admin workload.
- Hosting is deliberately deferred until the application is implemented and its local functionality is verified. Keep the FastAPI backend and scheduled/background processing provider-portable. Select a provider only after evaluating the completed workload, dependencies, scheduling, reliability, deployment effort and total cost.
- No hosting provider, paid service, deployment or external resource is approved by this setup decision.
