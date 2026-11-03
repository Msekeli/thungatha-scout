# M2 — Backend Foundation and Scout Supabase Persistence

**Status:** Not started  
**Updated:** 3 November 2026  
**Depends on:** M0 — Repository Audit and Scope Lock

## Outcome

A runnable, provider-portable Python backend with a dedicated Scout Supabase PostgreSQL project, reproducible schema, protected configuration, health endpoint and tested persistence boundary. This milestone establishes the foundation for the Greenhouse vertical slice.

## Scope

- FastAPI HTTP API foundation.
- React + TypeScript + Vite + Tailwind CSS v3 frontend skeleton.
- Supabase Auth client foundation; backend-side JWT validation is required before protected API access.
- Dedicated Scout Supabase project connection.
- Schema/migration strategy for employers and employer sources first.
- Configuration and secret handling.
- Health/readiness endpoint and consistent API error responses.
- Repository test setup and database integration coverage.
- Clear separation between Scout operational data and Thungatha publication destination.

Do not provision Azure resources, upgrade Azure subscriptions, create paid infrastructure or make production deployment changes during M2 without explicit user approval.

## Checkpoints

### M2-C01 — Repository and runtime baseline
**Status:** In review

Inspect the live dev tree, existing Python experiments, dependency/runtime constraints and local development setup. Preserve existing code and evidence. Confirm the smallest runnable backend layout.

**Exit criteria**
- Current backend/frontend tree and relevant existing implementations are inventoried.
- Python runtime and hosting compatibility assumptions are documented.
- No duplicate application skeleton is introduced.
- Local startup approach is documented.


**Inspection findings — M2-C01 (4 November 2026)**

The live `dev` tree was inspected through GitHub. No local checkout was available in this execution environment, so runtime commands were not run.

**Current backend inventory**
- `backend/pyproject.toml` defines a setuptools package, Python `>=3.11`, FastAPI, Pydantic Settings and Uvicorn. Development extras are HTTPX, pytest and Ruff. Pytest is configured for `test-suites/unit-tests` and `test-suites/integration-tests`.
- `backend/scout/main.py` creates the FastAPI application and exposes `GET /health`.
- `backend/scout/settings.py` owns the current Pydantic Settings configuration and cached settings factory.
- `backend/test-suites/unit-tests/test_health_endpoint.py` is the only backend test currently present.
- `backend/registry/ats-adapter-registry.json` and `backend/registry/employer-source-registry.json` are separate data registries and remain outside the Python package.
- `backend/.env.example` contains non-secret local settings. No database client, migration tool, repository, auth validator or ATS adapter is currently present in this `dev` backend.

**Frontend inventory**
- `frontend/` is a Vite + React 18 + TypeScript 5.7 + Tailwind CSS v3 skeleton.
- `@supabase/supabase-js` is present for the browser authentication client. The frontend README correctly states that backend JWT validation and authorization are still required.
- The frontend has a package manifest and entry files, but no dependency lockfile was found in the inspected directory listing. A build has not been run.

**Historical implementation preservation**
- `setup/backend-prototype` contains the earlier employer-discovery and Greenhouse analysis/discovery/jobs modules, verification and site-investigation code, tests, and `backend/data/companies.csv`.
- `feature/cape-town-greenhouse-workday-api` contains a Workday client, a previous jobs API experiment and corresponding tests.
- `research` contains additional discovery output and reports.
- These branches are evidence and source material, not current `dev` application code. No wholesale merge or copy is justified. Review individual adapter behavior and tests when their implementation checkpoints begin. Preserve the company CSV and historical reports.

**Backend structure decision for the new implementation**
Keep the existing `backend/scout` import package and FastAPI entry point. Do not create a second `backend/app` application or migrate the scaffold solely to imitate a layered template. Keep the initial composition root and configuration small. As real capabilities are implemented, keep these responsibilities separate:
- HTTP layer: request/response validation, route handlers and authentication dependencies; no ATS or persistence business rules in route handlers.
- Application layer: employer/source registration, adapter orchestration and vacancy-processing use cases.
- Domain layer: employer/source/vacancy concepts, state transitions and deterministic eligibility rules.
- ATS integrations: one reusable implementation per supported platform, driven by employer/source registry configuration rather than employer-specific code.
- Persistence boundary: repositories and database-specific implementation kept behind application-facing interfaces; no database calls from route handlers or ATS adapters.
- Runtime composition/configuration: dependency construction and environment settings, without embedding business rules.

Do not create these packages as empty placeholders. Add a package or module only when its first concrete responsibility is implemented. Avoid a generic service/repository framework, dependency-injection container, queue or ORM until a demonstrated requirement exists. Keep scheduled processing separately executable from the HTTP API while reusing the same application use cases.

**Runtime and hosting assumptions**
- The repository declares Python 3.11 or newer. The actual local interpreter version and successful installation/startup are not verified in this environment.
- Local startup documented by the backend README is: from `backend/`, create/activate a virtual environment, run `pip install -e ".[dev]"`, then `uvicorn scout.main:app --reload`. The health route is `GET /health`.
- Keep API and scheduled processing provider-portable. No hosting provider is selected in C01; hosting remains deferred until local runtime, browser/scraping dependencies and scheduled execution requirements are tested.
- No Supabase project was provisioned or contacted. Database availability and credentials remain unverified.

**C01 outcome:** The current `scout` package is the smallest suitable starting point. No duplicate application skeleton or speculative directories are needed. C01 is **In review** pending user review; this record does not claim a local runtime or frontend build pass.

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
- FastAPI is explicitly approved for the HTTP API. Do not add queues, an ORM, cloud services or additional infrastructure without a separate demonstrated need and approval.
- Do not mark a checkpoint Accepted without actual evidence and user acceptance.
