# M2 — Backend Foundation and Scout Supabase Persistence

**Status:** Not started  
**Updated:** 3 November 2026  
**Depends on:** M0 — Repository Audit and Scope Lock

## Outcome

A runnable, provider-portable Python backend with a dedicated Scout Supabase PostgreSQL project, reproducible schema, protected configuration, health endpoint and tested persistence boundary. This milestone establishes the foundation for the Greenhouse vertical slice.

## Scope

- Python HTTP API foundation.
- Dedicated Scout Supabase project connection.
- Schema/migration strategy for employers and employer sources first.
- Configuration and secret handling.
- Health/readiness endpoint and consistent API error responses.
- Repository test setup and database integration coverage.
- Clear separation between Scout operational data and Thungatha publication destination.

Do not provision Azure resources, upgrade Azure subscriptions, create paid infrastructure or make production deployment changes during M2 without explicit user approval.

## Checkpoints

### M2-C01 — Repository and runtime baseline
**Status:** Not started

Inspect the live dev tree, existing Python experiments, dependency/runtime constraints and local development setup. Preserve existing code and evidence. Confirm the smallest runnable backend layout.

**Exit criteria**
- Current backend/frontend tree and relevant existing implementations are inventoried.
- Python runtime and hosting compatibility assumptions are documented.
- No duplicate application skeleton is introduced.
- Local startup approach is documented.

### M2-C02 — Backend application foundation
**Status:** Not started

Create the minimal Python HTTP application and configuration boundary. Keep HTTP handlers thin and business logic in ordinary application modules. Preserve portability so the hosting provider can be selected without rewriting domain logic.

**Exit criteria**
- Backend starts locally with example configuration.
- Health endpoint reports application readiness without exposing secrets.
- Consistent validation and error response contract exists.
- No real credentials are committed.

### M2-C03 — Scout Supabase schema and persistence
**Status:** Not started

Connect only to the dedicated Scout Supabase project. Define migrations and repositories for employer and employer-source records first. Do not create the entire speculative schema before its query patterns and API needs are understood.

**Exit criteria**
- Schema/migrations are reproducible.
- Employer and source identity/constraints are tested.
- Backend owns privileged database writes.
- Scout credentials are separate from Thungatha credentials.
- No frontend service-role credentials exist.

### M2-C04 — Data boundary and publishing contract
**Status:** Not started

Inspect Thungatha's current database contract before defining the publication projection. Document stable identifiers, required fields, idempotency and destination error handling. Do not publish during this checkpoint.

**Exit criteria**
- Scout operational schema is isolated.
- Thungatha destination contract is documented against actual schema evidence.
- Raw/rejected/exception/history records are excluded from the destination projection.
- Publishing remains disabled until its own milestone.

### M2-C05 — Verification and checkpoint review
**Status:** Not started

Add unit and database integration tests for the foundation. Record actual commands and results. Review secrets, migrations, error handling and provider portability.

**Exit criteria**
- Relevant unit and integration tests pass.
- No secrets or privileged frontend credentials are committed.
- Local setup instructions are accurate.
- User reviews the checkpoint evidence.

## Implementation constraints

- Follow AGENTS.md, CODING-STANDARDS.md, CHATGPT-PROJECT-GUIDE.md, THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md and TECHNICAL-APPROACH.md.
- Keep modules focused and within repository line limits.
- Do not add FastAPI, queues, an ORM, cloud services or additional infrastructure without demonstrating the need.
- Do not mark a checkpoint Accepted without actual evidence and user acceptance.
