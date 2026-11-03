# Thungatha Scout — Implementation Plan

**Status:** Active delivery roadmap  
**Updated:** 3 November 2026  
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

| Responsibility | Technology / hosting |
|---|---|
| Admin frontend | React + TypeScript + Vite on Vercel |
| Backend API and scheduled processing | Python, hosted on a cost-appropriate provider; keep portable |
| Scout operational database | Dedicated Supabase PostgreSQL project |
| Thungatha publication destination | Existing Thungatha Supabase PostgreSQL project |
| ATS integrations | Greenhouse and Workday adapters |

Azure Table Storage is not a v1 requirement. Azure Functions may be reconsidered after a real cost/hosting comparison; do not provision Azure resources or upgrade the exhausted student subscription without explicit approval.

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

## 5. Milestones

| Milestone | Name | Status |
|---|---|---|
| M0 | Repository Audit and Scope Lock | Accepted |
| M1 | Employer Discovery and Source Registry | In progress; research retained, not a blocker for first vertical slice |
| M2 | Backend Foundation and Scout Supabase Persistence | Not started |
| M3 | Employer Registration and Greenhouse Adapter | Not started |
| M4 | Workday Adapter and Tenant Compatibility | Not started |
| M5 | React Admin — Employer and Source Management | Not started |
| M6 | Vacancy Quality Pipeline and Exception Review | Not started |
| M7 | Automated Scheduling and Thungatha Publishing | Not started |
| M8 | Security, Hosting, Recovery and Release Acceptance | Not started |

### M2 — Backend foundation and Scout Supabase persistence
Deliver a runnable Python backend, configuration/secrets boundary, Scout Supabase schema/migrations, health endpoint, API error contract, test setup and initial repositories.
Acceptance: local startup; reproducible schema; connectivity test; employer/source persistence through backend services; no secrets committed.

### M3 — Employer registration and Greenhouse
URL-first Greenhouse source inspection, employer metadata preview/confirmation, idempotent registration, meaningful source test and vacancy retrieval.
Acceptance: supported URL parsing; reliable metadata or manual fallback; duplicates prevented; pagination and failure outcomes tested.

### M4 — Workday adapter
Reusable host/tenant/site parsing and tested CXS retrieval.
Acceptance: DigiOutsource plus at least one additional tenant tested before broad compatibility is claimed; pagination, detail retrieval and failure states covered.

### M5 — React admin
Vite/React/TypeScript private admin with Dashboard, Companies, Vacancies and Exceptions. Add Company is URL-first. Source health and extraction history are embedded in company detail.
Acceptance: authenticated API use; employer/source add, edit, test, pause/resume/archive; responsive states; no privileged browser credentials.

### M6 — Quality pipeline and exception review
Normalisation, source-scoped identity, content hashing, version history, deterministic freshness/completeness/location/application URL/duplicate checks, exception queue and auditable decisions.
Acceptance: qualifying records auto-eligible; hard failures suppressed; uncertain cases held; unchanged records do not create versions; failed/partial runs do not expire vacancies.

### M7 — Scheduling and publishing
Bounded recurring extraction, concurrency protection, retries/backoff, run metrics, source health, and idempotent publication to Thungatha.
Acceptance: unattended run works; only gate-passing records publish; duplicate publishing prevented; failed publication recovers; destination receives only required clean fields.

### M8 — Security, hosting and release
Authentication/authorization, secret handling, deployment, monitoring, retention, backup/recovery, rollback and end-to-end verification.
Acceptance: deployed frontend/backend; production configuration verified; critical flows tested; costs reviewed; user accepts release.

## 6. Immediate sequence

1. Re-inspect the current `dev` repository and preserve existing work.
2. Confirm the separate Scout Supabase project is available; do not create paid resources.
3. Define the Scout schema and Thungatha publishing contract.
4. Implement M2 backend foundation and persistence.
5. Build Greenhouse vertical slice, then Workday.
6. Build React admin against the stable API.
7. Implement quality gates and exception workflow.
8. Add unattended scheduling and idempotent publishing.
9. Deploy only after hosting costs, backups and failure recovery are understood.

## 7. Acceptance and evidence

Use statuses: Not started, In progress, Blocked, In review, Accepted. Never mark work accepted without recorded checks/evidence and explicit user acceptance. Record exactly which commands were run; do not claim tests or deployments that were not performed.
