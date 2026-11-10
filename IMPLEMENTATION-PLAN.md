# Thungatha Scout — Implementation Plan

**Status:** Active delivery roadmap  
**Updated:** 10 November 2026  
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

V1 ATS adapter: Greenhouse. Workday is deferred from active investigation and implementation until further notice. Initial geographic scope: Cape Town. No public job-search frontend or recruiter self-service.

## 3. Current architecture

| Responsibility                       | Technology / hosting                                                                                                                          |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Admin frontend                       | React + TypeScript + Vite + Tailwind CSS v3; hosting pending                                                                                  |
| Backend API and scheduled processing | FastAPI (Python), separately executable workers; provider pending                                                                             |
| Scout operational database           | Dedicated Supabase PostgreSQL project                                                                                                         |
| Thungatha publication destination    | Existing Thungatha Supabase PostgreSQL project                                                                                                |
| ATS integrations                     | Greenhouse reference adapter; Lever integrated and accepted; Workday deferred                                                                              |
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

| Milestone | Name                                               | Status                                                                                                                                       |
| --------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| M0        | Repository Audit and Scope Lock                    | Accepted                                                                                                                                     |
| M1        | Employer Discovery and Source Registry             | In progress; runs in parallel with implementation                                                                                            |
| M2        | Backend Foundation and Scout Supabase Persistence  | In progress; checkpoint review/remaining contract work                                                                                       |
| M3        | Greenhouse Vertical Slice                          | In progress — user confirms extraction-to-Thungatha flow has been exercised; remaining Greenhouse/admin acceptance evidence must be recorded |
| M4        | ATS Adapter Expansion                              | In progress — Ashby deferred; Lever M4-LEVER-A and M4-LEVER-B accepted; next: Teamtailor                                                  |
| M5        | Cross-cutting Admin UI and API Integration         | In progress alongside M3 and M4 when its checkpoints begin                                                                                   |
| M6        | Fourth-Employer Compatibility Test                 | Not started                                                                                                                                  |
| M7        | Vacancy Quality, Lifecycle and Exception Review    | Not started                                                                                                                                  |
| M8        | Scheduling and Thungatha Publishing                | Not started                                                                                                                                  |
| M9        | Security, Hosting, Recovery and Release Acceptance | Not started                                                                                                                                  |
| M10       | Docker Containerisation and Packaging              | Not started                                                                                                                                  |

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

### M4 — First-wave ATS adapter expansion

M4 is limited to the six first-wave adapters: Ashby, Lever, Teamtailor, Personio, Recruitee and Workable. It contains exactly twelve checkpoints, two per adapter, as defined in `milestones/M4-ATS-ADAPTER-EXPANSION.md`.

For each adapter, complete the checkpoints in order:

- **A — Investigate, design and implement.** First inspect real employer sources and prove the public retrieval behavior. Record the evidence and file-by-file design before writing code; the investigation activity does not commit code. Once the method and design are established, implement the adapter and focused unit tests within the same A checkpoint. If no permitted, reliable method is established, record an evidence-backed blocked/deferred outcome.
- **B — Integrate and verify.** Register generic adapter capabilities and employer-specific source configuration in the correct registries; connect the adapter to the shared extraction/persistence and existing API/admin workflow; add contract/integration coverage; run regression and mandatory repository checks; perform representative live validation; record exact evidence and results.

Complete and review both checkpoints for one adapter before starting the next adapter. Do not split these responsibilities into additional checkpoints.

The six first-wave providers and target cohorts are:

- **Ashby:** Midnite, MyEdSpace, Tree Traction — public Job Postings API.
- **Lever:** Mama Money, Theodo, Wing Assistant — public Postings API; verify regional host and pagination.
- **Teamtailor:** Root Platform, Footasylum, TeamViewer — public RSS feed and custom-domain handling.
- **Personio:** ottonova, Open, Openprovider — public XML feed when enabled by the employer.
- **Recruitee:** TransPerfect, Fastned, Tether — verify current public XML offer feed availability; do not rely on the token-protected Careers Site API.
- **Workable:** LekkeSlaap, Electrum, GoTyme Bank — validate observed public careers-widget JSON behavior.

Greenhouse remains the existing architectural reference and is not part of M4 delivery. SmartRecruiters, BambooHR, Breezy HR, Simplify.hr, eRecruit/Neptune, Zoho Recruit and SAP SuccessFactors belong to later-wave planning, not this milestone. Placement Partner is a separate recruitment/staffing source pipeline and is not part of M4. Workday remains deferred.

Across all adapters, keep provider HTTP, parsing, pagination and detail retrieval inside the adapter; keep quality gates, deduplication, lifecycle and publishing shared. Do not hardcode employer-specific slugs or tenant identifiers in adapter code. HTTP 200 alone is not acceptance: verify meaningful vacancy content, full descriptions where expected, complete-board counts, stable IDs and exact candidate destinations. Failed or partial runs must not imply that vacancies disappeared.

**Acceptance:** all six adapters have completed their A/B checkpoints or have evidence-backed blocked/deferred outcomes; implemented adapters are registered and integrated through the shared workflow; relevant unit, contract, integration and regression tests pass; representative live evidence and gaps are recorded; adding another employer to a supported platform requires configuration rather than employer-specific adapter code. Follow the 100-physical-line limit and mandatory naming/line-limit checks for all handwritten source and test files.

### M5 — Cross-cutting admin UI and API integration

This milestone runs alongside M3 and M4. It is not a gate that begins only after both adapters are complete.

Deliver the private React admin incrementally:

- Admin app foundation, Supabase Auth sign-in and protected routes.
- Companies and sources list/detail workflows.
- URL-first Add Company flow: paste URL, detect supported ATS, preview metadata/configuration, allow manual fallback, confirm employer/source relationship.
- Source connection test, operational status and useful error feedback.
- Progressive Greenhouse integration and first-wave ATS adapters as each API contract stabilises. Workday remains deferred.
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

### M10 — Docker containerisation and packaging

This is a final packaging checkpoint, not an early development dependency. Start only after the full application, API, scheduled worker and critical workflows pass local verification without Docker.

- Add a backend Dockerfile and `.dockerignore` using the existing Python dependency/configuration setup.
- Build one reusable backend image; support separate API and scheduled-worker commands without duplicating application code.
- Keep Scout Supabase and Thungatha Supabase external; do not add a database container.
- Pass secrets and environment-specific settings at runtime; never bake credentials into the image.
- Verify image build, API startup/health, worker execution, graceful shutdown, timeout handling and database connectivity locally.
- Document local build/run commands and the eventual host's runtime requirements.

Acceptance: both API and worker run successfully from the same versioned image in local container tests; no credentials are embedded; application behavior matches the already accepted non-container local run. Docker packaging does not itself authorize cloud deployment or paid resources.

### M9 — Security, hosting, recovery and release

Complete authentication/authorization, secret handling, hosting-provider evaluation, deployment, monitoring, retention, backup/recovery, rollback and end-to-end verification.

Hosting selection is intentionally deferred until the application is implemented and verified locally. Evaluate the actual API, scheduled-worker, scraping and runtime requirements before selecting a provider.

Acceptance: one-email Supabase Auth restriction verified; public registration disabled; backend independently enforces the email allowlist; deployed frontend/backend; production configuration verified; critical flows tested; costs reviewed; user accepts release.

## 7. Immediate execution sequence

1. Finish the outstanding M2 review items using the current repository and test evidence. Do not redo completed persistence work.
2. Close any remaining M2 API/error and publishing-contract decisions as separate, bounded checkpoints; keep Scout operational persistence separate from Thungatha's destination.
3. Continue M3: complete registry schema/loading/validation and the common adapter contract; extend Greenhouse inspection into persisted extraction and vacancy listing.
4. Complete the Greenhouse backend slice and connect the admin workflow: retrieve and persist full descriptions, inspect a selected vacancy in the Jobs workspace, and verify the draft Thungatha payload without publishing.
5. Implement M4 in the ranked waves recorded in `docs/ATS-PLATFORM-RESEARCH.md`; start with the easy public feeds/endpoints, retain hard platforms and Placement Partner in the documented backlog, and use the shared adapter contract.
6. Run the six-employer validation cohort, keeping each verification claim evidence-backed and pending where necessary.
7. Run the held-out fourth-employer compatibility test through the admin UI.
8. Build the quality/lifecycle/exception pipeline, then scheduling and idempotent publishing.
9. Verify the complete application locally before evaluating hosting, cost, backups and deployment.
10. Add Docker containerisation as a final packaging checkpoint after local application and worker acceptance; build one backend image with separate API and scheduled-worker commands, then verify both locally.

## 8. Acceptance and evidence

Use statuses: Not started, In progress, Blocked, In review, Accepted. Never mark work accepted without recorded checks/evidence and explicit user acceptance. Record exactly which commands were run; do not claim tests or deployments that were not performed. Keep each checkpoint bounded, reviewable and reversible.

## Operating-model correction — 9 November 2026

The older implementation steps requiring employer/source verification, source permission decisions, company approval, Cape Town presence checks, or vacancy-by-vacancy approval are superseded.

Current acceptance requirements:

- Company and source registration is direct, without approval/verification states.
- Greenhouse and Lever URLs are detected from pasted careers/board URLs and register employers outside the static registry.
- South African relevance is evaluated per vacancy location, never from employer country or headquarters.
- Only South African vacancies are exported to Thungatha; all is an internal unfiltered view and must not be the publication default.
- Admin can permanently delete a company and archive a vacancy. No other approval workflow is required.
- Preserve source previews and extraction-run history as operational diagnostics.
- Keep provider adapters isolated and the shared ingestion/export pipeline maintainable.


## M4 status update — 10 November 2026

Lever's M4-LEVER-A and M4-LEVER-B checkpoints are accepted. The user verified the live admin workflow: Lever employers registered through both the frontend and backend configuration paths have extracted vacancies persisted and visible in the Companies and Jobs views.

Regression evidence supplied by the user: backend unit suite **160 passed**; frontend typecheck and production build passed; frontend source line-limit and naming checks passed. See `milestones/M4-ATS-ADAPTER-EXPANSION.md` for the checkpoint evidence.

Continue M4 with **M4-TEAMTAILOR-A**. Ashby remains deferred pending its partner response. M4 as a whole remains in progress until the remaining first-wave adapters reach accepted or evidence-backed deferred outcomes.
