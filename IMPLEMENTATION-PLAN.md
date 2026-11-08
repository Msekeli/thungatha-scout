# Thungatha Scout — Implementation Plan

**Status:** Active delivery roadmap  
**Updated:** 5 November 2026  
**Branch:** `dev`

## 1. Authority

- `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md` owns current product and architecture decisions.
- `TECHNICAL-APPROACH.md` describes the current implementation design.
- `CHATGPT-PROJECT-GUIDE.md` is the concise operating brief for ChatGPT Project work.
- `AGENTS.md` and `CODING-STANDARDS.md` govern all repository contributors and coding agents.
- Older milestone notes and research reports remain historical evidence. Where they conflict with the latest dated decision record, the latest decision record wins.

## 2. Product outcome

Scout is an unattended employer-sourced vacancy ingestion and publishing system for Thungatha. The administrator mainly adds employers by pasting official careers/ATS URLs and confirming employer/source identity. Scout then retrieves, validates, normalises, deduplicates, tracks and publishes qualifying vacancies automatically.

Human review is exception-based, not a mandatory approval step for every vacancy. Only records that pass deterministic publication gates are published. Uncertain or incomplete records are held for review.

V1 ATS adapters: Greenhouse and Workday. Initial geographic scope: Cape Town. No public job-search frontend or recruiter self-service.

## 3. Current architecture

| Responsibility                       | Technology / hosting                                                                                                                          |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Admin frontend                       | React + TypeScript + Vite + Tailwind CSS v3; hosting pending                                                                                  |
| Backend API and scheduled processing | FastAPI (Python), separately executable workers; provider pending                                                                             |
| Scout operational database           | Dedicated Supabase PostgreSQL project                                                                                                         |
| Thungatha publication destination    | Existing Thungatha Supabase PostgreSQL project                                                                                                |
| ATS integrations                     | Greenhouse and Workday adapters                                                                                                               |
| Admin authentication                 | Supabase Auth; one configured administrator email only, public registration disabled; backend validates JWTs and enforces the email allowlist |

Azure Table Storage is not a v1 requirement. Keep the backend provider-portable and defer hosting selection until local implementation and workload verification are complete. Do not provision paid resources or upgrade the exhausted student subscription without explicit approval.

Scout and Thungatha databases are isolated. Scout retains raw operational, rejected, exception and history records. Only qualified published records cross to Thungatha.

## 4. Operating rules

- Employer/source onboarding requires administrator confirmation of identity and official source relationship.
- After activation, scheduled extraction and publication operate unattended.
- Auto-publication requires all configured hard quality gates to pass.
- Missing application URL, insufficient content, uncertain location, unresolved duplicate, malformed data, suspicious content or low-confidence classification creates an exception.
- Do not equate official ATS provenance with vacancy quality.
- AI can assist with extraction/classification but cannot bypass deterministic gates or fabricate evidence.
- Every automated decision is auditable.
- Failed/partial extraction cannot mark vacancies removed or expired.
- Publishing is idempotent and recoverable.
- No service-role credentials in the frontend.
- Repository-wide architecture limits: no handwritten source file may exceed 100 physical lines; descriptive naming conventions are strictly enforced across backend and frontend.

## 5. Delivery model

Build the product in **vertical slices**. A capability is not considered delivered merely because its adapter or API function works in isolation: expose it through the backend API, connect the relevant admin workflow, and verify the end-to-end path as soon as the underlying contract is stable.

Frontend and backend are therefore **cross-cutting implementation work**, not sequential silos. The admin foundation and shared UI patterns can be established early; each employer/source capability is then integrated progressively as its backend endpoint becomes available. Do not build a large disconnected frontend ahead of the API, and do not postpone all frontend work until both adapters are complete.

Employer discovery and source verification continue in parallel with implementation. Research findings remain evidence until independently verified and recorded in the source registry; they do not block the first vertical slice.

## 6. Milestones

| Milestone | Name                                               | Status                                                                                                                                                     |
| --------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M0        | Repository Audit and Scope Lock                    | Accepted                                                                                                                                                   |
| M1        | Employer Discovery and Source Registry             | In progress; runs in parallel with implementation                                                                                                          |
| M2        | Backend Foundation and Scout Supabase Persistence  | In progress; checkpoint review/remaining contract work                                                                                                     |
| M3        | Greenhouse Vertical Slice                          | In progress — generic board-candidate resolution with Greenhouse metadata validation and detection-only onboarding implemented; local verification pending |
| M4        | Workday Vertical Slice                             | Not started                                                                                                                                                |
| M5        | Cross-cutting Admin UI and API Integration         | In progress alongside M3 and M4 when its checkpoints begin                                                                                                 |
| M6        | Fourth-Employer Compatibility Test                 | Not started                                                                                                                                                |
| M7        | Vacancy Quality, Lifecycle and Exception Review    | Not started                                                                                                                                                |
| M8        | Scheduling and Thungatha Publishing                | Not started                                                                                                                                                |
| M9        | Security, Hosting, Recovery and Release Acceptance | Not started                                                                                                                                                |

### M2 — Backend foundation and Scout Supabase persistence

Deliver a runnable Python backend, configuration/secrets boundary, Scout Supabase schema/migrations, health endpoint, API error contract, test setup and initial repositories.

Acceptance: local startup; reproducible schema; connectivity test; employer/source persistence through backend services; documented API error behaviour; no secrets committed.

Close the persistence checkpoint using actual local/cloud test evidence. Define the Thungatha publishing boundary separately; do not mix destination credentials or tables into Scout persistence. Do not mark any checkpoint Accepted without explicit user approval.

### M3 — Greenhouse vertical slice

Deliver the reusable Greenhouse adapter and first complete employer/source workflow.

Checkpoints:

- Registry schemas, loading and validation.
- Common ATS adapter contract.
- Greenhouse URL inspection and board configuration extraction from careers-page links, embeds, inline API configuration and generic employer/domain candidates. Validate candidate tokens against public Greenhouse board metadata and the supplied employer identity; a `gh_jid` value is a job ID, not a board token. Do not require an individual job URL or employer-specific code. Persist the pasted careers page as source evidence, separately from the employer homepage URL.
- Greenhouse vacancy retrieval, complete-board validation, full `content=true` description handling, and normalisation. The public Job Board list endpoint returns all published jobs; validate `meta.total` rather than inventing page-based pagination.
- Backend API endpoints for source inspection, preview, connection test and retrieval.
- Admin URL-entry uses one Add Company action: detect/validate the ATS board as part of submission, register the employer/source, then start vacancy extraction. Detection must not retrieve vacancies. Show progress during remote discovery, confirm company/source registration immediately, and run vacancy extraction in the background with a later imported-count or failure notification in Companies. Keep registration copy neutral; do not present named employers as supported examples.
- Jobs workspace supports selecting a vacancy to inspect its full description and a clearly labelled draft Thungatha payload preview; inspection does not publish.
- Vacancy management includes a dedicated detail endpoint, separate original-job and apply links, review states (pending, needs verification, verified, rejected), review notes, and soft archive/restore. Lifecycle status remains separate from operator review status.
- Employer branding persistence includes optional logo URL and source URL fields; the company profile can maintain those URLs and the admin displays a logo when supplied. Logo discovery/verification remains a separate follow-up.
- Validate the three selected Greenhouse employers using live evidence. The current candidate cohort is Takealot Group, Impact.com and Ozow; each employer/source relationship, Cape Town presence and live retrieval capability must be verified independently. Pending claims remain pending.

Acceptance: adding another Greenhouse employer requires registry configuration, not employer-specific adapter code; supported URL forms, complete-board counts, full descriptions, meaningful vacancy data and failure outcomes are tested; the admin can complete source onboarding, extraction and vacancy inspection end to end.

### M4 — Workday vertical slice

Deliver a reusable Workday adapter and integrate it into the same employer/source workflow.

Checkpoints:

- Parse and validate host, tenant and site independently.
- Implement observed public CXS retrieval and pagination.
- Retrieve detail data where required and normalise vacancies.
- Expose Workday inspection, preview, test and retrieval through the backend API.
- Integrate Workday into the existing admin workflow; do not create a separate Workday-only UI.
- Validate DigiOutsource plus the other two selected Workday employers, Old Mutual and Pick n Pay, using live evidence. Treat unverified host/tenant/site values as hypotheses until tested.

Acceptance: DigiOutsource and at least two additional tenants are tested before broad compatibility is claimed; pagination, detail retrieval, empty results, blocked/rate-limited responses, malformed responses and partial failures are covered. Adding a tenant requires configuration, not employer-specific code.

### M5 — Cross-cutting admin UI and API integration

This milestone runs alongside M3 and M4. It is not a gate that begins only after both adapters are complete.

Deliver the private React admin incrementally:

- Admin app foundation, Supabase Auth sign-in and protected routes.
- Companies and sources list/detail workflows.
- URL-first Add Company flow: paste URL, detect supported ATS, preview metadata/configuration, allow manual fallback, confirm employer/source relationship.
- Source connection test, operational status and useful error feedback.
- Progressive Greenhouse and Workday integration as each API contract stabilises.
- Dashboard, vacancies and exception/review views when their backend capabilities are ready.
- Vacancy detail, review, and archive/restore controls integrated against the management API.

Acceptance: the admin uses authenticated backend APIs; backend independently enforces the administrator allowlist; source add/edit/test/pause/resume/archive works; no service-role key or privileged credential reaches the browser. Each delivered vertical slice has an end-to-end test.

### M6 — Fourth-employer compatibility test

Select a held-out employer not used to implement the adapters. Paste its official careers/ATS URL through the admin workflow.

Acceptance: Scout detects and configures the supported ATS, previews the source, retrieves meaningful vacancies and registers the source without employer-specific code changes. Record any unsupported URL patterns or manual fallback required. This is the generalisation test, not another implementation cohort.

### M7 — Vacancy quality, lifecycle and exception review

Implement normalisation, source-scoped identity, content hashing, vacancy version history, deterministic freshness/completeness/location/application URL/duplicate checks, exception queue and auditable decisions.

Acceptance: qualifying records become auto-publish eligible; hard failures are suppressed; uncertain cases are held; unchanged records do not create versions; failed/partial runs do not expire vacancies; lifecycle reconciliation requires a sufficiently complete successful inventory.

### M8 — Scheduling and Thungatha publishing

Implement bounded recurring extraction at 06:00 and 18:00 `Africa/Johannesburg` time, with a maximum one-hour execution window per run (06:00–07:00 and 18:00–19:00). The one-hour limit is a ceiling, not a target: finish and exit as soon as assigned work completes. Add concurrency protection, per-source progress, bounded retries/backoff, run metrics, source health and idempotent publishing to Thungatha.

Acceptance: unattended run works; only records passing publication gates publish; duplicate publishing is prevented; failed publication recovers; destination receives only required clean fields. Keep Scout and Thungatha persistence isolated.

### M9 — Security, hosting, recovery and release

Complete authentication/authorization, secret handling, hosting-provider evaluation, deployment, monitoring, retention, backup/recovery, rollback and end-to-end verification.

Hosting selection is intentionally deferred until the application is implemented and verified locally. Evaluate the actual API, scheduled-worker, scraping and runtime requirements before selecting a provider.

Acceptance: one-email Supabase Auth restriction verified; public registration disabled; backend independently enforces the email allowlist; deployed frontend/backend; production configuration verified; critical flows tested; costs reviewed; user accepts release.

## 7. Immediate execution sequence

1. Finish the outstanding M2 review items using the current repository and test evidence. Do not redo completed persistence work.
2. Close any remaining M2 API/error and publishing-contract decisions as separate, bounded checkpoints; keep Scout operational persistence separate from Thungatha's destination.
3. Continue M3: complete registry schema/loading/validation and the common adapter contract; extend Greenhouse inspection into persisted extraction and vacancy listing.
4. Complete the Greenhouse backend slice and connect the admin workflow: retrieve and persist full descriptions, inspect a selected vacancy in the Jobs workspace, and verify the draft Thungatha payload without publishing.
5. Implement Workday and connect it to the same admin workflow.
6. Run the six-employer validation cohort, keeping each verification claim evidence-backed and pending where necessary.
7. Run the held-out fourth-employer compatibility test through the admin UI.
8. Build the quality/lifecycle/exception pipeline, then scheduling and idempotent publishing.
9. Verify the complete application locally before evaluating hosting, cost, backups and deployment.

## 8. Acceptance and evidence

Use statuses: Not started, In progress, Blocked, In review, Accepted. Never mark work accepted without recorded checks/evidence and explicit user acceptance. Record exactly which commands were run; do not claim tests or deployments that were not performed. Keep each checkpoint bounded, reviewable and reversible.
