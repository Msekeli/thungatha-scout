# Thungatha Scout — Master Implementation Plan

**Document status:** Active implementation roadmap; M0 accepted  
**Purpose:** milestone order, scope, dependencies, progress and acceptance tracking  
**Product:** Thungatha Scout  
**Parent product:** Thungatha  
**Repository:** https://github.com/Msekeli/thungatha-scout  
**Branch:** dev

## 1. Purpose and authority

This document defines delivery milestones and acceptance criteria. THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md owns established product decisions. TECHNICAL-APPROACH.md defines the v1 implementation approach. Detailed checkpoint definitions, evidence, unresolved issues and user-review records belong under milestones/.

## 2. Product boundary

Scout is a private employer/source and vacancy operations system supporting Thungatha. It registers employer career sources, retrieves vacancies through supported ATS adapters, normalises and tracks vacancy versions, supports human review and publishes approved records to Thungatha.

V1 is limited to Greenhouse and Workday, with a private Next.js admin interface. No public job-search frontend, recruiter self-service, complex multi-user administration or autonomous AI approval.

## 3. Delivery principles

- Work on dev only unless explicitly instructed otherwise.
- Inspect the live repository and current tests before implementation. Preserve historical evidence and existing work.
- Python Azure Functions is the authoritative backend for business rules and persistence. Next.js is the admin UI and calls the backend API; it does not write directly to PostgreSQL.
- Use one Function App, one PostgreSQL operational database and a small adapter contract.
- Implement Greenhouse and Workday only for v1. Adding an employer to an existing adapter is configuration, not new adapter code.
- Keep employer, source, vacancy, vacancy version, review and extraction-run responsibilities distinct.
- Source operational status and computed health are separate. Employer/source approval and vacancy approval are separate.
- A failed or incomplete extraction must never expire vacancies. Expiry requires a sufficiently complete successful comparison.
- Preserve provenance and history. Archive rather than destructively cascade-delete.
- Use deterministic code for URL parsing, deduplication, state transitions and publishing. AI cannot approve or publish.
- Keep Azure usage bounded. Do not provision paid services or recurring workloads without approval.
- Record only tests and commands actually run. No milestone is accepted without evidence and explicit user review.

## 4. Milestone roadmap

| Milestone | Name | Status |
|---|---|---|
| M0 | Repository Audit and Scope Lock | Accepted |
| M1 | Employer Discovery and Source Registry | In progress — research retained; not a blocker for first vertical slice |
| M2 | Backend Foundation and PostgreSQL Persistence | Not started |
| M3 | Employer Registration and Greenhouse Adapter | Not started |
| M4 | Workday Adapter and Tenant Compatibility | Not started |
| M5 | Admin Company Management and Source Operations | Not started |
| M6 | Vacancy Normalisation, Versioning and Review | Not started |
| M7 | Scheduling, Health, Recovery and Publishing | Not started |
| M8 | Security, Release Verification and Acceptance | Not started |

## 5. Milestone definitions

### M0 — Repository Audit and Scope Lock
**Status:** Accepted. Repository inventory and scope review are documented in milestones/M0-AUDIT-REPORT.md. The current dev scaffold was previously found not to contain a runnable backend or frontend application. Recheck before implementation; do not assume later changes have not occurred.

### M1 — Employer Discovery and Source Registry
**Status:** In progress. Preserve existing discovery research, evidence models and registry separation. Broader dual-channel employer discovery remains valuable but is not a prerequisite for starting source registration and extraction. For the first product slice, an administrator can supply a known employer ATS URL. ATS-footprint discovery must not be represented as a global customer directory. Keep C01/C02 evidence and open issues; do not rewrite historical reports or claim acceptance. Re-scope remaining M1 work after the first extraction slice is working.

### M2 — Backend Foundation and PostgreSQL Persistence
**Outcome:** A runnable Python Azure Functions v2 application, configuration/secrets boundary, PostgreSQL connection and migration strategy, health endpoint, API error contract, test setup and minimal persistence models.
**Exit criteria:**
- Backend starts locally using documented configuration.
- PostgreSQL schema/migrations are reproducible.
- Health endpoint and database connectivity are tested.
- Employer/source records can be persisted and read through backend services.
- Unit tests and a database integration test pass.
- No secrets are committed.

### M3 — Employer Registration and Greenhouse Adapter
**Outcome:** URL-first employer registration supports Greenhouse board URLs, metadata preview/confirmation, source validation and vacancy retrieval using the documented public Job Board API.
**Exit criteria:**
- Greenhouse URL/token parsing handles supported URL forms and invalid inputs.
- Board metadata is retrieved and employer name presented for confirmation; logo is best-effort.
- Registration is idempotent and prevents duplicate employer/source records.
- Adapter retrieves paginated job listings and required job details/content where available.
- Empty board, invalid board, rate limit, timeout and malformed response are distinct outcomes.
- Contract/integration tests include fixtures; live smoke test is separately recorded.

### M4 — Workday Adapter and Tenant Compatibility
**Outcome:** A reusable Workday adapter parses host, tenant and site from a supplied careers URL and retrieves vacancies through tested public careers-site CXS behavior.
**Exit criteria:**
- DigiOutsource URL is the first compatibility case.
- Tenant and site are parsed separately and verified against the target endpoint.
- Listing pagination and individual posting details are tested.
- At least one additional Workday board is tested before claiming broad compatibility.
- Tenant-specific behavior uses explicit tested strategies inside one adapter, not employer-specific classes.
- Undocumented endpoint limitations and access/terms questions are recorded honestly.

### M5 — Admin Company Management and Source Operations
**Outcome:** A private Next.js admin panel provides dashboard and company CRUD/source management using the Python API.
**Exit criteria:**
- Navigation contains Dashboard, Companies, Vacancies and Review Queue.
- Add Company accepts a URL, detects supported ATS, allows manual override, previews extracted metadata and requires admin confirmation.
- Company names are extracted where reliable; manual entry is a fallback.
- Company list/detail supports edit, add source, test, pause/resume and archive.
- Source health and extraction history are embedded in Company Details.
- UI has loading, empty, validation and error states; privileged endpoints are authenticated/authorized.

### M6 — Vacancy Normalisation, Versioning and Review
**Outcome:** Extracted vacancies are normalised, deduplicated, versioned and presented for explicit human review.
**Exit criteria:**
- Stable source-scoped external identity is enforced.
- Normalised SHA-256 fingerprints detect meaningful content changes.
- Latest extracted content is separate from approved/published content.
- Meaningful changes enter review without silently replacing an approved version.
- Lifecycle status is separate from approval/publication status.
- Failed/incomplete extraction cannot expire vacancies.
- Admin can inspect, preview, approve and reject; decisions are audited.

### M7 — Scheduling, Health, Recovery and Publishing
**Outcome:** Bounded scheduled extraction and reconciliation produce source health and run metrics, and approved records publish idempotently to Thungatha.
**Exit criteria:**
- Runs record start/end, outcome, duration, counts, pagination/completeness and safe diagnostics.
- Source operational status is distinct from computed health (unknown/healthy/warning/failed).
- Retry/backoff and concurrency are bounded; overlapping runs are prevented.
- Only sufficiently complete successful inventory comparisons can expire vacancies.
- Only approved/validated vacancy versions publish.
- Publishing is idempotent and failures are recoverable without duplicates.
- Cost and usage limits are documented.

### M8 — Security, Release Verification and Acceptance
**Outcome:** Release checks cover authentication, authorization, secret handling, deployment configuration, data integrity, operational recovery and user acceptance.
**Exit criteria:**
- Backend and frontend production builds/tests pass.
- Critical registration, extraction, review and publishing flows are tested.
- No service-role key or backend secret is exposed to browser code.
- Database backup/retention and archive behavior are documented.
- Deployment and rollback instructions are verified.
- User explicitly accepts the release.

## 6. Status rules

Use only: Not started, In progress, Blocked, In review, Accepted. Acceptance requires evidence, actual checks/results, documented remaining gaps and explicit user review. Do not mark a milestone accepted because files exist or code has been generated.

## 7. Change control

1. Record material scope or architecture changes in the source of truth and this plan.
2. Preserve prior evidence; clarify it with dated records rather than erasing history.
3. Update detailed milestone checkpoints when scope or acceptance criteria change.
4. Distinguish observed fact, hypothesis, decision and open question.
5. Do not overwrite reports or historical data without reviewed migration.
6. Keep changes reviewable and work on dev.

## 8. Immediate execution order

1. Re-inspect dev and confirm actual scaffold and tool versions.
2. Implement M2 backend/database foundation and define the API contract.
3. In parallel, scaffold the Next.js admin shell against a documented API contract; connect it when endpoints exist.
4. Complete Greenhouse registration/extraction (M3).
5. Complete DigiOutsource Workday compatibility (M4).
6. Finish company/source CRUD (M5), then vacancy review/versioning (M6).
7. Add scheduling, health, safe expiry and Supabase publishing (M7).

The first demonstrable outcome is: paste a Greenhouse or DigiOutsource Workday URL, inspect the source, confirm employer metadata, register the company/source and retrieve real vacancies. Do not spend another planning cycle before beginning M2.
