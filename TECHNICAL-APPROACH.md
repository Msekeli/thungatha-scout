# Thungatha Scout — Technical Approach

**Status:** Current v1 implementation baseline  
**Updated:** 3 November 2026

## 1. Product model

Scout is an unattended employer-sourced vacancy ingestion and publishing system supporting Thungatha. The administrator's main recurring action is adding an employer by pasting an official careers/ATS URL and confirming the employer/source identity. Once a source is verified and activated, Scout operates automatically.

Routine human approval of every vacancy is not part of the operating model. Human attention is reserved for exceptions and administrative control.

V1 adapter target is the registry catalogue: Greenhouse, Workday, Lever, Breezy HR and Ashby. Greenhouse is the reference flow already exercised through publication to Thungatha; M4 expands the same adapter contract to the remaining four. Initial geography is Cape Town. Scout is not a public job-search frontend and has no recruiter self-service.

## 2. Deployment architecture

| Component            | Technology                                      | Hosting                          |
| -------------------- | ----------------------------------------------- | -------------------------------- |
| Admin UI             | React, TypeScript, Vite, Tailwind CSS v3        | Hosting provider pending         |
| Backend API          | FastAPI (Python)                                | Hosting provider pending         |
| Crawler worker       | Crawlee for Python; standalone scheduled script | Zyte Scrapy Cloud (student unit) |
| Operational database | PostgreSQL via Supabase                         | Dedicated Scout Supabase project |
| Public destination   | Existing Thungatha Supabase/PostgreSQL          | Existing Thungatha project       |

Zyte Scrapy Cloud is approved for the crawler worker only under the user's GitHub Student Developer Pack entitlement. Keep Crawlee as the crawler framework. Scrapy Cloud requires a Scrapy-compatible project package for standalone Python scripts; Scrapy is only the deployment wrapper, not a replacement crawler. The worker must call existing Scout services and persist to the Scout database. API and frontend hosting remain undecided. Do not share Scout's operational schema/database with Thungatha or use MongoDB/Azure Table Storage in v1.

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
2. Backend normalises and validates the URL and detects one of the configured registry adapters (Greenhouse, Workday, Lever, Breezy HR or Ashby).
3. If detection is uncertain, admin can choose/override a platform whose adapter has passed verification.
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

The shared implementation boundary lives in `scout.ats_adapters.ats_adapter_contracts`:

- `ATSAdapter` defines configuration-based retrieval and adapter cleanup.
- `ATSAdapterResult` carries the outcome, completeness and normalized vacancies.
- `NormalizedVacancy` carries provider-independent identity, content, location,
  department, application URL, timestamps and the retained raw provider payload.

`SourceExtractionService` selects an adapter factory using the source's
`adapter_key`, records the extraction run, and hands normalized vacancies to the
shared persistence layer. Provider-specific HTTP and field mapping remain inside
the corresponding `ats_adapters/<provider>_adapter/` package. Unexpected adapter
exceptions are recorded as failed extraction outcomes; they are not treated as an
empty board. Adding another provider should require an adapter implementation and
factory registration, not a new persistence path.

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

Common listing route: `https://{host}/wday/cxs/{tenant}/{site}/jobs`. Validate each tenant. Test DigiOutsource, Old Mutual and Pick n Pay before claiming broad compatibility. HTTP 200 alone is not a successful source test.

### Lever

The registry records the public postings endpoint `https://api.lever.co/v0/postings/{slug}?mode=json` as a candidate. Verify board discovery, response completeness, pagination behavior, rate limits and representative employer records before approving the adapter.

### Breezy HR

The registry currently has no verified retrieval endpoint or configuration schema. Investigate official developer documentation and actual hosted career portals/widgets first. Implement only after the retrieval contract, access constraints and employer linkage are evidenced.

### Ashby

The registry currently has a candidate slug configuration but no verified endpoint. Establish the public job-board retrieval contract and response shape from official documentation and live employer evidence before implementation.

`placement_partner` is separately catalogued for recruitment/staffing sources. It is not part of the direct-employer ATS adapter set and must remain a separate ingestion path.

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

Use a hosted scheduler/worker mechanism appropriate to the chosen backend host. The initial vacancy extraction schedule is 06:00 and 18:00 in the `Africa/Johannesburg` timezone. Each run has a maximum execution duration of one hour (06:00–07:00 and 18:00–19:00); this is a hard ceiling, not a target runtime. The worker must exit immediately when its assigned work is complete, whether that takes 15 minutes, 30 minutes or the full hour. Never add artificial waiting to consume the window. Prevent overlapping executions with a durable lock/lease. Apply bounded per-source timeouts, retries, exponential backoff and rate-limit handling. Persist progress and outcomes per source so completed work is not needlessly repeated. Record run completeness, counts, actual duration and sanitised diagnostics. A timeout or failed/partial source must not be treated as a complete inventory or mass-suppress/expire vacancies. Keep the schedule and one-hour ceiling configurable; measure actual runtime after the full workflow is implemented.

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

Unit tests cover URL parsing, adapters, config validation, normalisation, hashing, duplicate handling, quality gates, state transitions and idempotency. Contract tests use recorded ATS fixtures. PostgreSQL integration tests cover schema constraints and persistence. Live smoke tests for every registry ATS adapter are separately recorded. Greenhouse is the reference end-to-end flow; Workday, Lever, Breezy HR and Ashby require representative live validation.

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

## Architecture quality and maintainability standards

- Every handwritten application source-code file across both backend and frontend must remain at 100 physical lines or fewer.
- Directory and file names must communicate domain responsibility using descriptive kebab-case (frontend) and snake_case (backend Python) conventions.
- Monolithic containers are prohibited; UI pages compose focused presentation components, custom feature hooks, resource-specific API clients, and modular stylesheets.
- Quality gates are enforced by `scripts/check-file-line-limits.py` and `scripts/check-naming-conventions.py`.

## Current operating model override — 9 November 2026

The company/source approval workflow described elsewhere in this document is obsolete.

1. Company and source registration has no approval, verification, evidence, or permission states.
2. Greenhouse and Lever are URL-detected adapters. A pasted supported ATS board URL must be sufficient to derive board configuration and register the source, including employers absent from the static employer registry.
3. Employer location is metadata only. Vacancy eligibility is decided from the vacancy's own location.
4. South Africa is the default and publication scope. Export queries must explicitly filter South African vacancy locations; they must not treat south_africa as equivalent to all.
5. Admin actions are limited to permanent company deletion and vacancy archiving. Source previews and extraction history remain operational diagnostics.
6. Keep the architecture adapter-based and shared. New employers on an existing ATS require configuration, not new adapter code.

## 13. Careers-page crawler and platform routing — 11 November 2026 (superseded 12 November 2026)

Scrapy is the default bounded HTTP crawler for employer careers-page discovery, redirect/link inspection, ATS fingerprinting and generic public HTML/JSON extraction. It is complementary to ATS adapters, not a replacement. When a known ATS is detected, route the source to its existing adapter. Do not scrape the same board through a parallel generic pipeline.

Use Playwright only when inspection proves that browser execution is required; inspect public network requests first and prefer a stable, permitted JSON/feed endpoint. The crawler records requested/final/canonical URLs, content type, source fingerprint evidence, public job links, crawl timestamps, completeness and explicit outcomes. Bound domain depth, page count, response size, concurrency, timeouts and retries. Respect robots.txt, site terms, access controls and rate limits. Do not bypass login walls, CAPTCHAs or other restrictions.

Crawl observations and vacancies flow through the existing Scout backend and PostgreSQL repositories, normalized vacancy contract, source-scoped identity, quality/lifecycle pipeline and publication ledger. The crawler never writes directly to Thungatha and does not introduce another database. Failed or partial crawls cannot imply vacancy expiry. Full HTML snapshots are not retained by default.

Scrapy Cloud (Zyte) is a candidate managed runner through the GitHub Student Developer Pack, subject to verification of the current offer and limits. Spiders must run locally; keep scheduling and deployment configuration portable. Do not enable recurring hosted workloads or paid usage until eligibility, quotas and cost are confirmed.

South African platform investigation order and employer evidence are maintained in `docs/CAREER-PAGE-CRAWLER-IMPLEMENTATION.md`. SAP SuccessFactors (Sanlam and Capitec leads), Workday and Oracle Recruiting Cloud lead the enterprise investigation. Simplify.hr, eRecruit, BambooHR, Breezy HR and Workable lead the local/mid-market investigation. These are candidates until current employer relationships and public retrieval behavior are independently verified. Greenhouse remains the proven reference adapter; existing Lever and Teamtailor work is retained.

## 14. Crawlee and AI enrichment architecture — 12 November 2026

The user-approved crawler framework is **Crawlee for Python**, superseding the previous Scrapy proposal. Crawlee runs inside Scout's separately executable worker; it is not a new microservice or a commitment to Apify hosting.

### Crawling responsibilities

- HTTP-first bounded retrieval for official employer careers pages, redirects, relevant links, public HTML/JSON and platform fingerprints.
- Playwright browser crawling only when evidence demonstrates that normal HTTP retrieval and a permitted public endpoint are insufficient.
- Configurable domain/depth/request/concurrency/response-size/time limits, bounded retries and explicit crawl outcomes.
- Respect robots.txt, applicable terms, access controls and rate limits. Do not bypass login walls, CAPTCHAs or blocks.
- Known ATS sources route to the existing adapter selected from the registry. Never retrieve a known board twice through both an ATS adapter and generic crawler.
- Generic extraction is restricted to public non-standard career pages without a suitable existing adapter.
- Crawl observations enter existing Scout application services, PostgreSQL persistence, normalized vacancy contract, quality/lifecycle pipeline and publication ledger. No second database or direct Thungatha writes.

### AI provider responsibilities

Gemini and Groq are interchangeable implementations behind a small provider interface. Deterministic extraction and normalization run first. AI is used selectively for difficult description structuring or genuinely ambiguous extraction/classification.

Configure one primary provider and optional fallback. Do not call both providers for every record. Cache validated results by input/content hash and prompt/schema version. Bound input characters, output tokens, timeouts and retries. Validate structured responses; preserve source content and send unresolved/low-confidence cases to existing exception handling.

AI is not authoritative for source permission, employer approval, vacancy identity, lifecycle, quality-gate overrides or publishing. API keys are server-side secrets. AI and crawler are disabled by default until local configuration and smoke tests are completed.

### Dependencies and configuration

Backend optional dependency groups:

- `crawler`: Crawlee with its Playwright integration.
- `ai`: Google GenAI SDK and Groq SDK.
- `dev`: existing pytest and Ruff tooling.

Install the full local development set from `backend/` with `python -m pip install -e ".[dev,crawler,ai]"`. Copy/update the local `.env` from `.env.example`; never commit `.env` or API keys. Model identifiers are configured explicitly rather than silently assumed by code. Keep all runtime limits configurable and validated by Pydantic settings.

Detailed routing, investigation waves and acceptance criteria live in `docs/CAREER-PAGE-CRAWLER-IMPLEMENTATION.md`. No Apify hosting, paid AI plan, paid crawler execution or recurring cloud workload is approved by this architecture decision.
