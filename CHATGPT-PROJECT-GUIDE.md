# ChatGPT Project Guide — Thungatha Scout

Use this document as the operating brief for ChatGPT conversations and implementation tasks in this repository. It is a concise project context, not a replacement for source code, milestone evidence or coding standards.

## Product objective

Build Thungatha Scout as an unattended employer-sourced vacancy ingestion and publishing system. The administrator's main routine action is to paste official employer careers/ATS URLs, confirm employer identity and source relationship, and activate sources. Scout should then run without routine vacancy-by-vacancy approval.

V1 scope: South Africa-wide vacancy eligibility; Greenhouse and Workday adapters; private admin UI; automated extraction, validation, deduplication, exception handling and publishing. No public job-search frontend and no recruiter self-service.

## Current decisions — do not silently change

- Frontend: React + TypeScript + Vite + Tailwind CSS v3. Hosting is deferred pending local verification.
- Backend: FastAPI (Python) HTTP API plus separately executable scheduled/background processing. Keep provider-portable; hosting provider remains undecided.
- Frontend styling: Tailwind CSS v3 for layout and responsive structure; global CSS design tokens and semantic component classes in `frontend/src/styles/` own colours, surfaces, borders, shadows and status treatments. Avoid hardcoded visual palette utilities inside components.
- Admin authentication: Supabase Auth, restricted to the one configured administrator email. Public sign-up/registration is disabled. Backend independently validates JWTs and checks the email allowlist for every protected operation; store the allowlisted email server-side. Browser uses only the Supabase URL and publishable/anon key.
- Hosting: deliberately undecided until the application is implemented and verified locally. Keep FastAPI and scheduled/background processing provider-portable; choose hosting after measuring actual runtime, scraping dependencies, scheduling, reliability and cost. Do not add provider-specific infrastructure or paid resources before that decision.
- Scout operational database: a dedicated Supabase PostgreSQL project.
- Thungatha destination: the existing Thungatha Supabase PostgreSQL project.
- Do not use MongoDB or Azure Table Storage in the current v1 architecture.
- Do not put Scout's raw/uncleaned/exception/history data in Thungatha. Publish only clean records passing the deterministic gates.
- Greenhouse and Workday only in v1. Do not add ATS providers without explicit scope approval.
- The Azure for Students credit is exhausted. Never assume Azure hosting/storage is free. Do not upgrade subscriptions or provision paid Azure resources without explicit user approval and a cost estimate.
- Supabase Free is suitable only for development/low-volume evaluation until inactivity pausing, backups, capacity and production reliability are addressed.
- Vacancy extraction schedule: 06:00 and 18:00 `Africa/Johannesburg` time. Each run has a maximum one-hour window and must stop as soon as its assigned work is complete; one hour is a ceiling, not a target. Do not force runs to consume the window. Prevent overlap and preserve per-source progress on partial/time-limited runs.
- Work on branch `dev` only unless the user explicitly instructs otherwise.

## Product workflow

1. Admin pastes an official careers/ATS URL.
2. Backend detects Greenhouse/Workday, inspects source metadata and returns a preview.
3. Admin confirms employer identity, Cape Town evidence and official source relationship.
4. Source is activated after meaningful retrieval validation.
5. Scheduled workers retrieve vacancies.
6. Deterministic code normalises, fingerprints, deduplicates and evaluates vacancies.
7. Gate-passing vacancies publish automatically and idempotently to Thungatha.
8. Hard failures are suppressed with a reason. Uncertain/incomplete cases enter an exception queue.
9. Admin can inspect exceptions, reject/unpublish, correct permitted fields, retry, pause/resume sources and archive records.

An official ATS is provenance, not a guarantee of vacancy quality. A vacancy must have a meaningful title/description, credible South African location or explicit South Africa remote eligibility, usable application destination, stable identity, valid content and no unresolved high-confidence duplicate. Unknown location is not automatically Cape Town. Failed/partial extraction never expires jobs.

AI may assist with extraction/classification but cannot invent evidence or bypass hard gates. Deterministic code owns identity, URLs, deduplication, freshness, state transitions and publishing. Record the reason/evidence/rule version for every automated decision.

## Data boundary

Scout Supabase stores employers, sources, vacancy observations/versions, extraction runs, quality outcomes, exceptions, audit events and publishing ledger. Thungatha Supabase stores only the public-facing employer/vacancy projection required by the main application. Keep separate credentials and schemas/projects. Backend only for privileged writes; never expose service-role keys in browser code.

Avoid retaining full HTML snapshots by default. Use bounded retention for any raw evidence. Do not create a new version for unchanged content. Preserve useful audit history and archive rather than cascade-delete.

## Working method

- Read `AGENTS.md`, source of truth, implementation plan, active milestone, technical approach and coding standards before implementation.
- Inspect the live `dev` tree and relevant code/tests; do not assume prior summaries describe current files.
- State the current milestone/checkpoint and intended outcome.
- Make small, focused changes. Do not restart architecture planning unless implementation evidence reveals a real issue.
- Preserve historical experiments and reports. Do not claim absent historical code is present.
- Add tests for changed behavior and report exact commands/results. If tests are not run, say so.
- Do not provision paid services, change subscriptions, deploy production or delete data without explicit approval.
- Update source of truth, implementation plan and milestone records when a product decision changes.
- Never mark a milestone Accepted without evidence and explicit user acceptance.
- Report branch, changed files, commit, verification and remaining gaps.

## Immediate implementation direction

1. Confirm the separate Scout Supabase project and inspect Thungatha's existing publishing schema.
2. Define Scout's PostgreSQL schema and explicit Thungatha publishing contract.
3. Implement the Python backend foundation and persistence.
4. Implement Greenhouse, then Workday.
5. Build the React admin against the backend API.
6. Implement deterministic quality gates and exception review.
7. Add unattended scheduling, idempotent publishing, deployment and recovery.

The user prefers concise, direct guidance, maintainable code, low operating cost and no unnecessary abstractions. Do not ask the user to repeat decisions already recorded here.
