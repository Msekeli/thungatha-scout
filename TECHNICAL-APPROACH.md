# Thungatha Scout — Technical Approach

**Status:** V1 implementation baseline  
**Date:** 3 November 2026  
**Branch:** dev  
**Scope:** Greenhouse and Workday employer-source registration, vacancy extraction and private administration

## 1. Objective

Deliver an internal system that lets an administrator register an employer by pasting its careers/ATS URL, inspect and confirm employer/source details, retrieve vacancies through a supported adapter, monitor the source and manage employer/source records.

The model is company-centric: employers are durable business records; ATS sources are independently managed connections; vacancies retain employer and source provenance. V1 supports Greenhouse and Workday only.

## 2. Technology and ownership

| Area | Technology | Responsibility |
|---|---|---|
| Admin frontend | Next.js App Router, TypeScript, Tailwind CSS | Dashboard and company/vacancy operations UI |
| Backend | Python Azure Functions v2, one Function App | HTTP API, business rules, adapters and scheduled triggers |
| Operational database | PostgreSQL | Employers, sources, vacancies, versions, runs and audit records |
| Publishing destination | Existing Thungatha Supabase integration | Approved records only |

Python owns business rules and authoritative persistence. Next.js calls the backend API; it does not connect directly to PostgreSQL or duplicate business rules. Azure Functions HTTP handlers are thin and delegate to application services. Timer triggers call the same services. No microservices or separate Function Apps per ATS.

## 3. Core relational model

### employers
- id, name, normalized_name
- logo_url and logo attribution/source metadata (nullable)
- website_url and location evidence (nullable)
- organization_type: direct employer, agency, staffing, hybrid, other or unresolved
- status: pending_review, approved, rejected or archived
- created_at, updated_at, archived_at

### employer_sources
- id, employer_id
- ats_platform: greenhouse or workday in v1
- source_url
- source_config JSONB for platform-specific identifiers/configuration
- operational_status: pending_verification, active, paused or archived
- health_status: unknown, healthy, warning or failed (computed from extraction history)
- last_success_at, last_failure_at, created_at, updated_at, archived_at

One employer may have multiple sources. A source belongs to one employer. Registration must be idempotent and prevent duplicate employers/sources.

### vacancies
- id, employer_id, source_id
- external_job_id, source_job_url, application_url
- title, location, employment_type, description
- lifecycle_status: active, possibly_expired, expired, removed, unavailable or needs_review
- review_status: pending, approved or rejected
- current_version_id and approved_version_id
- first_seen_at, last_seen_at, expired_at
- content_hash: SHA-256 of normalised review-relevant content
- Unique constraint on (source_id, external_job_id)

### vacancy_versions
Store materially different extracted content versions, content hash, observed timestamp and provenance. Keep latest extracted content separate from the version approved/published. A changed version must not silently overwrite the previously approved version.

### extraction_runs
Store source_id, started_at, completed_at, duration_ms, status (success/partial/failed), jobs_found, jobs_added, jobs_updated, jobs_expired, pages_fetched, inventory_complete and sanitised diagnostic details.

### review/audit records
Record actor, entity, prior/new state, timestamp, decision and reason. Human approval is persisted backend state, not merely a UI interaction.

### Referential integrity and deletion
Use foreign keys and restrictive deletion behavior to protect history. Employer/source removal in v1 means archive/disable, not physical cascading deletion. Archiving a source must not delete its employer, vacancies or extraction runs.

## 4. Add Company workflow

1. Admin opens Companies and selects Add Company.
2. Admin pastes the careers/ATS URL.
3. Backend validates/normalises the URL and attempts ATS detection.
4. If detection is inconclusive, UI offers Greenhouse/Workday manual selection or correction. Unsupported URLs are not silently forced into an adapter.
5. Adapter inspects the board and returns a structured preview: detected platform, employer name if available, source identifiers/configuration, logo candidate, test outcome and sample vacancy count.
6. Admin confirms employer identity and source relationship. If the name cannot be reliably extracted, ask for manual confirmation/input as a fallback.
7. Backend checks for an existing employer/source and registers idempotently.
8. Source remains pending verification until meaningful retrieval testing and required source approval are complete. Activate only after admin confirmation.

Employer identity, official employer/source relationship, Cape Town presence, technical retrieval, source terms/permission and human approval are separate claims. Technical success does not prove the other claims.

## 5. Adapter contract and ATS behavior

The shared adapter contract supports source URL identification/parsing, configuration validation, employer/board metadata retrieval, paginated vacancy inventory retrieval and individual vacancy detail retrieval where needed.

Adapters own HTTP transport, platform response parsing and pagination. They do not own employer approval, vacancy review, deduplication policy, lifecycle decisions or publishing.

Outcomes distinguish success with results, success with zero results, not found, blocked, rate limited, timeout/transient failure, malformed response and partial/incomplete retrieval.

### Greenhouse

Use the documented public Job Board API for a known board token:
- Board metadata: GET /v1/boards/{board_token}
- Jobs: GET /v1/boards/{board_token}/jobs?content=true

Parse supported Greenhouse URL forms and extract the board token. Retrieve board metadata before registration confirmation. The API is board-specific, not a global customer directory. Verify actual logo fields in the returned payload; logo absence is not a registration failure. Follow documented pagination and response behavior.

### Workday

Workday is an undocumented public careers-site integration, not a guaranteed public API. Parse hostname, tenant and site separately. For:

https://myhcm.wd3.myworkdayjobs.com/digioutsource

Expected configuration:
- host: myhcm.wd3.myworkdayjobs.com
- tenant: myhcm
- site: digioutsource

The commonly observed CXS listing route is:

https://{host}/wday/cxs/{tenant}/{site}/jobs

Validate this against the live board, use bounded requests, handle pagination and retrieve individual posting details through returned source paths where supported. Do not assume every Workday tenant behaves identically. Add explicit, tested compatibility strategies inside the single Workday adapter only when evidence requires them. DigiOutsource is the first case; test at least one additional tenant before claiming broad compatibility.

A successful HTTP status alone is not success. Validate response shape and vacancy records. A zero-vacancy board is valid if the endpoint and board identity are verified.

## 6. Employer metadata and logos

Employer identity extraction priority:
1. authoritative ATS board metadata;
2. official careers-page metadata/structured data;
3. validated public board/CXS response metadata;
4. administrator confirmation/input when uncertain.

Never derive a company name solely from a URL slug.

Logo retrieval is best-effort: verified ATS image, official employer website, separately evaluated provider after checking availability/pricing/terms, then administrator upload/replacement. Do not depend on Clearbit Logo API. Store logo source/attribution. A missing logo never blocks registration or extraction.

## 7. Extraction, normalisation and versioning

1. Retrieve a complete or explicitly partial source inventory.
2. Validate/map fields into the common vacancy model.
3. Normalise HTML and whitespace; calculate SHA-256 over review-relevant fields such as title, description, location and employment type.
4. Match by (source_id, external_job_id); URL is supporting evidence, not a replacement for stable source identity.
5. New vacancy: persist first version as pending review.
6. Unchanged vacancy: update last_seen_at; do not create a version or review item.
7. Changed vacancy: create a version and mark for review when materially relevant. Preserve the previously approved/published version.
8. Missing vacancy: transition lifecycle only after a sufficiently complete successful inventory comparison. Failed or partial runs cannot expire jobs.

Do not deduplicate across employers solely on title or description.

## 8. Source operations and health

Operational status is pending_verification, active, paused or archived. Health is derived from recent extraction outcomes: unknown, healthy, warning or failed. A source may be active but unhealthy. Paused/archived sources are not scheduled.

Show source test results in Company Details: detected employer, ATS, identifiers, validation result, jobs retrieved, response time, test timestamp and sanitised errors.

## 9. Admin UI v1

Navigation: Dashboard, Companies, Vacancies and Review Queue. Source health, tests and extraction history are embedded in Company Details.

Companies supports search/list/detail, Add Company, edit permitted metadata, add source, test source, pause/resume and archive. Add Company is URL-first and does not routinely require manual company-name entry.

Vacancies supports search/filter and inspection. Review Queue supports source-content inspection, Thungatha presentation preview, permitted field edits, approve/reject and decision reason. Employer/source approval and vacancy approval are separate.

All admin operations require authentication and backend authorization. No privileged credential is exposed to browser code.

## 10. Scheduling, failures and publishing

Use bounded Azure Functions timer triggers for scheduled extraction. Choose initial cadence after observing source count, runtime and Azure cost. Prevent overlapping runs per source; apply bounded timeouts, retries and backoff.

Only a sufficiently complete successful inventory can drive missing-vacancy reconciliation. Failed/partial runs record diagnostics and leave vacancy lifecycle unchanged.

Publish only approved, validated versions to Thungatha through an idempotent integration contract. Keep Scout operational state separate from the destination. Publishing failures must be retryable without duplicate destination records.

## 11. Testing strategy

- Unit tests: URL parsing, adapter selection, configuration validation, normalisation, hashing, state transitions and deduplication.
- Adapter contract tests using recorded Greenhouse and Workday fixtures.
- PostgreSQL integration tests for migrations, constraints and repositories.
- Live smoke tests for Greenhouse and DigiOutsource Workday, recorded separately from deterministic tests.
- Failure cases: empty board, malformed payload, timeout, rate limit, partial pagination, duplicate/changed vacancy, failed reconciliation and publishing retry.
- UI tests for registration, confirmation, duplicate handling, company/source actions and vacancy review.
- Explicitly prove failed/partial extraction cannot expire jobs and unapproved versions cannot publish.

## 12. V1 exclusions

No recruiter portal/submissions, public job-search frontend, ATS beyond Greenhouse and Workday, one adapter per employer, autonomous approval, speculative agents, global ATS customer-directory assumption, direct frontend database writes or destructive historical deletion.

## 13. First vertical-slice acceptance

1. Open admin UI and paste a Greenhouse board URL.
2. Scout identifies Greenhouse, retrieves board metadata/vacancies and presents employer details for confirmation.
3. Repeat with DigiOutsource Workday URL.
4. Confirm/register both employers/sources without employer-specific adapter code.
5. Display registered companies and retrieved vacancies in the admin UI.
6. Show meaningful source-test results and persist extraction-run evidence.

This is a target, not a claim that it is implemented or verified. Live endpoint assumptions must be tested before being treated as supported behavior.
