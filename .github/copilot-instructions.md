# GitHub Copilot Instructions — Thungatha Scout

Use the repository-root `AGENTS.md` as the authoritative contributor contract. Read it before making changes. Also consult `CHATGPT-PROJECT-GUIDE.md`, `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`, `IMPLEMENTATION-PLAN.md`, the active milestone document, `AI-WORKING-GUIDE.md` and `CODING-STANDARDS.md` as required by the task.

## Project context

Thungatha Scout is a private employer-sourced vacancy ingestion and publishing system for Thungatha. V1 supports Greenhouse and Workday, Cape Town scope, a private admin application, deterministic quality gates and exception-based human review. It is not a public job board. Do not expand scope or change architecture decisions without explicit approval.

Current stack:
- Backend: FastAPI, Python 3.11+, Pydantic Settings, Uvicorn.
- Backend package: `backend/scout/`; application services: `backend/scout/application/`.
- Persistence: Psycopg 3 and explicit SQL against the dedicated Scout Supabase PostgreSQL project; no ORM.
- Migrations: `backend/database-migrations/`.
- Tests: `backend/test-suites/unit-tests/` and `backend/test-suites/integration-tests/`.
- Frontend: React, TypeScript, Vite and Tailwind CSS v3.
- Work on branch `dev` only unless the user explicitly says otherwise.

## Required workflow

1. Identify the active milestone/checkpoint and its acceptance criteria.
2. Inspect the current branch, working tree, relevant source, tests, registries and milestone evidence before editing.
3. Read the applicable source-of-truth and architecture decisions. Do not replace evidence with assumptions.
4. Propose a concise plan before broad or multi-file changes. For investigation-only tasks, make no edits.
5. Make the smallest scoped change and add/update tests.
6. Every Python module directly in `backend/scout/application/` must remain at or below 100 lines. Do not compress code to satisfy the limit; split by responsibility. Ask for explicit review if the limit cannot be met cleanly.
7. Run the relevant tests, lint and type/build checks. Report only commands actually run and their observed results.
8. Review the diff for unrelated changes, secrets, destructive operations and contract drift.
9. Do not mark checkpoints Accepted. Acceptance belongs to the user.

## Non-negotiable constraints

- Keep Scout operational data and Thungatha destination data/credentials separate.
- Never expose service-role credentials or other backend secrets to frontend code.
- Do not publish records that fail deterministic gates. AI cannot invent evidence, approve sources, override gates or publish directly.
- Failed or partial extraction must never expire or remove vacancies.
- Preserve unresolved verification states; do not infer source permission, Cape Town presence or employer/source relationships from an ATS URL alone.
- Do not overwrite company registries, historical reports or user work without explicit review.
- Do not introduce new infrastructure, paid services, queues, ORMs, frameworks or speculative abstractions without demonstrated need and approval.
- Do not deploy, provision paid resources, delete data or perform destructive migrations without explicit approval.

For adapter work, inspect `backend/registry/ats-adapter-registry.json` and `backend/registry/employer-source-registry.json` before changing implementation. Keep generic adapter capabilities separate from employer-specific configuration.

At completion, report: checkpoint/status, changed files, exact verification commands/results, evidence and gaps, next action, and any user review/decision required.
