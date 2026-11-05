# Thungatha Scout

Thungatha Scout is an unattended employer-sourced vacancy ingestion and publishing system for Thungatha.

## Product workflow

The administrator mainly adds employers by pasting official careers/ATS URLs and confirming employer identity and source ownership. Scout then automatically retrieves, normalises, validates, deduplicates and publishes qualifying vacancies. Uncertain or incomplete records go to an exception-review queue; routine vacancy-by-vacancy approval is not required.

V1 adapters: Greenhouse and Workday. Initial geography: Cape Town. Scout is a private admin/operations system, not a public job-search frontend.

## Current architecture

- **Frontend:** React + TypeScript + Vite, hosted on Vercel.
- **Backend:** FastAPI (Python) HTTP API with separately executable scheduled/background processing. Keep it provider-portable; hosting selection is deferred until local implementation and workload verification are complete.
- **Scout operational data:** dedicated Supabase PostgreSQL project.
- **Thungatha destination:** existing Thungatha Supabase PostgreSQL project.
- **Admin authentication:** Supabase Auth, restricted to one configured administrator email; public registration is disabled and the backend enforces the allowlist.
- **Hosting:** frontend/backend provider decisions remain separate. Backend hosting is intentionally deferred until local implementation and workload verification are complete.
- **Data boundary:** Scout retains raw operational, rejected, exception and extraction-history records. Only records passing deterministic publication gates are sent to Thungatha.

Do not use MongoDB or Azure Table Storage for the current v1 baseline. Do not share the operational database between Scout and Thungatha. The browser never receives privileged database credentials.

## Repository guidance

Read `CHATGPT-PROJECT-GUIDE.md`, `AGENTS.md`, `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`, `IMPLEMENTATION-PLAN.md`, `TECHNICAL-APPROACH.md` and `CODING-STANDARDS.md` before substantial work. The latest dated decision record in the source of truth takes precedence over historical notes.

## Cost and deployment

The Azure for Students credit is exhausted. Do not upgrade it, provision Azure resources or create paid infrastructure without explicit approval and a cost estimate. Supabase Free is for development/low-volume evaluation only until inactivity, backup and production availability requirements are resolved.

See `TECHNICAL-APPROACH.md` for the current architecture and pipeline, and `IMPLEMENTATION-PLAN.md` for milestone status.
