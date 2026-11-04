# M2 — Backend Foundation and Scout Supabase Persistence

**Status:** In progress — M2-C01 in review  
**Updated:** 4 November 2026  
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

**Current backend inventory — refreshed 4 November 2026**

- `backend/pyproject.toml` defines a setuptools package for Python 3.11+, FastAPI, HTTPX, Pydantic Settings, Psycopg 3, PyJWT with cryptographic support and Uvicorn. Development extras include pytest and Ruff. Pytest discovers unit and integration suites under `backend/test-suites/`.
- `backend/scout/main.py` creates the FastAPI application, exposes `GET /health`, and registers RFC 9457-style Problem Details handlers for HTTP and request-validation errors.
- `backend/scout/settings.py` provides Pydantic Settings. Database and Supabase publishable-key values use `SecretStr`; the Supabase URL and configured administrator email are non-secret settings.
- `backend/scout/supabase_jwt.py` verifies asymmetric Supabase access tokens against the project's JWKS endpoint (ES256/RS256) and delegates legacy HS256 validation to Supabase Auth's `/auth/v1/user` endpoint. JWKS keys are cached for five minutes; the legacy path uses a five-second HTTP timeout.
- `backend/scout/authentication.py` exposes the `require_admin` FastAPI dependency. It rejects missing/invalid sessions, non-user tokens and users outside the configured single-email allowlist. Missing auth configuration fails closed with HTTP 503. Protected routes must explicitly depend on `require_admin`; the health endpoint remains public.
- `backend/scout/application/employer_service.py` defines employer/source creation payloads and service operations. Creation forces initial employer/source states and source permission to safe defaults rather than accepting approval state from the caller.
- `backend/scout/persistence/` contains the Psycopg connection boundary, migration runner and employer/source repositories.
- `backend/database-migrations/0001-create-employers-and-sources.sql` defines the initial employer/source schema, state constraints, evidence JSONB columns, foreign-key behavior and indexes.
- `backend/test-suites/unit-tests/` contains tests for health/error responses, settings, database connection configuration, migration discovery/checksums, employer/source payload validation, administrator authentication, Supabase JWT strategy selection and the application-module line limit.
- `backend/test-suites/integration-tests/test_supabase_persistence.py` is an opt-in cloud integration test. It must only use the dedicated Scout database, never the Thungatha destination.
- `backend/registry/` keeps ATS adapter definitions separate from employer/source mappings.
- `backend/.env.example` contains placeholder configuration only. No real credentials should be committed.

**Current frontend inventory**

- `frontend/` is a Vite + React 18 + TypeScript 5.7 + Tailwind CSS v3 skeleton with `@supabase/supabase-js`.
- `frontend/src/App.tsx` currently provides a minimal Supabase email/password sign-in and sign-out shell. It is not yet an admin application.
- `frontend/src/supabase.ts` uses only the browser Supabase URL and anon/publishable key. It does not contain a service-role credential.
- The frontend has no checked-in package lockfile in the inspected tree. A production build has not been run in this environment.
- Frontend sign-in is not sufficient authorization by itself. A backend JWT-verification and administrator allowlist dependency is now implemented, but no employer/source HTTP routes are exposed yet. Local execution and verification remain outstanding.

**Verification boundary**

The repository was inspected remotely through GitHub. No local checkout, Python test execution, Ruff run, frontend dependency installation/build, or live Scout Supabase connection was available in this work session. Code presence is not proof of runtime success. The opt-in database integration test remains unverified here.

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
**Status:** In progress — API error contract and administrator authentication implemented; local verification outstanding

Create the minimal Python HTTP application and configuration boundary. Keep HTTP handlers thin and business logic in ordinary application modules. Preserve portability so the hosting provider can be selected without rewriting domain logic.

**Exit criteria**
- Backend starts locally with example configuration.
- Health endpoint reports application readiness without exposing secrets.
- Consistent validation and error response contract exists.
- Protected routes can enforce verified Supabase user sessions and the configured administrator email allowlist.
- Missing auth configuration fails closed; no real credentials are committed.

### M2-C03 — Scout Supabase schema and persistence
**Status:** In progress — initial migration and repositories present; live verification outstanding

Connect only to the dedicated Scout Supabase project. Define migrations and repositories for employer and employer-source records first. Do not create the entire speculative schema before its query patterns and API needs are understood.

**Exit criteria**
- Schema/migrations are reproducible.
- Employer and source identity/constraints are tested.
- Backend owns privileged database writes.
- Scout credentials are separate from Thungatha credentials.
- No frontend service-role credentials exist.

### M2-C04 — Data boundary and publishing contract
**Status:** In review — destination contract mapped; transport decision deferred

Inspect Thungatha's current database contract before defining the publication projection. Document stable identifiers, required fields, idempotency and destination error handling. Do not publish during this checkpoint.

**Exit criteria**
- Scout operational schema is isolated.
- Thungatha destination contract is documented against actual schema evidence.
- Raw/rejected/exception/history records are excluded from the destination projection.
- Publishing remains disabled until its own milestone.

### M2-C05 — Verification and checkpoint review
**Status:** In progress — unit coverage expanded, including authentication; execution and review outstanding

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


### Administrator authentication implementation note — 4 November 2026

The backend now has an explicit Supabase Auth verification boundary:

- Configure `SCOUT_SUPABASE_URL`, `SCOUT_SUPABASE_PUBLISHABLE_KEY` and `SCOUT_ADMIN_EMAIL` in the backend environment. The publishable key is treated as a secret configuration value in backend settings; it is not a service-role key.
- ES256/RS256 access tokens are checked against the configured project's JWKS endpoint, with issuer, audience, expiry and required subject/time claims validated by PyJWT.
- Legacy HS256 tokens are validated by Supabase Auth's `/auth/v1/user` endpoint rather than trusting a locally configured JWT secret. This adds a bounded network call for that legacy signing mode.
- Only tokens representing authenticated user sessions with the configured administrator email are authorised. Email comparison is case-insensitive.
- The `require_admin` dependency is available for protected FastAPI routes. The health route intentionally remains public. Existing routes must opt in explicitly; authentication is not applied globally.
- Unit tests cover missing credentials, incomplete configuration, administrator acceptance, non-admin rejection, non-user token rejection, supported verification strategy selection and unsupported algorithms.

**Unverified:** the actual signing algorithm configured in the Scout Supabase project has not been inspected; no live JWT has been verified; no local tests or Ruff checks have been executed in this session. The project must have a valid Supabase Auth user for the configured administrator email, and public sign-up must be disabled/configured in the Supabase dashboard. No dashboard changes were made.


### M2-C04 contract inspection — 4 November 2026

The destination contract was inspected against the current `main` branch of the separate `Msekeli/thungatha` repository. This is a schema/code inspection only; no destination writes or credentials were used.

**Evidence inspected**
- `supabase/migrations/20261015000100_create_job_catalogue_and_user_states.sql`
- `supabase/migrations/20261016000100_job_ingestion_reliability.sql`
- `src/thungatha-features/job-discovery/server/schema.ts`
- `src/thungatha-features/job-discovery/server/ingestion.ts`
- `src/app/api/internal/jobs/ingest/route.ts`

**Destination projection**

Thungatha stores the public-facing job projection in `public.jobs` and source provenance in `public.job_sources`. The normalized contract in `normalizedJobSchema` uses camelCase JSON fields and requires nullable fields to be explicitly supplied as `null` where no value exists.

| Scout normalized field | Thungatha destination |
|---|---|
| `title` | `jobs.title` |
| `employerName` | `jobs.employer_name` |
| `description` | `jobs.description` |
| `locationText` | `jobs.location_text` |
| `countryCode` | `jobs.country_code` |
| `workMode` | `jobs.work_mode` |
| `employmentType` | `jobs.employment_type` |
| `salaryMin`, `salaryMax`, `salaryCurrency` | `jobs.salary_min`, `jobs.salary_max`, `jobs.salary_currency` |
| `providerKey`, `providerKind`, `externalJobId` | `job_sources.provider_key`, `provider_kind`, `external_job_id` |
| `upstreamSource` | `job_sources.upstream_source` |
| `sourceUrl`, `applicationUrl` | `job_sources.source_url`, `application_url` |
| `publishedAt` | `job_sources.published_at` |

Scout-only raw observations, extraction diagnostics, rejected records, exception records, internal evidence, decision history and quality-gate details are not part of this destination payload. Scout must reject or hold records before publication; the destination schema is not the Scout quality gate.

**Existing controlled write functions**

The destination migrations define these PostgreSQL functions:

- `start_job_ingestion_run(p_provider_key text, p_provider_kind text)` returns a run UUID.
- `persist_job_ingestion_batch(p_run_id uuid, p_jobs jsonb)` returns received/inserted/updated/skipped counts.
- `finish_job_ingestion_run(p_run_id uuid, p_status text, p_error_count integer, p_error_message text, p_received_count integer)` closes the run.

The functions use `SECURITY DEFINER`, an empty `search_path`, and explicitly revoke execution from `public`, `anon` and `authenticated`; execution is granted to `service_role`. The batch function checks that each payload's provider key and kind match the ingestion run. The destination also has a unique constraint on `(provider_key, external_job_id)` and performs upsert-style persistence.

**Provider identity requirement**

A single shared provider key such as `greenhouse` is unsafe for Scout because the destination uniqueness key is provider key plus external job ID. Different Greenhouse boards may reuse the same external job ID. The transport contract should therefore use a stable, source-specific provider key, derived from the immutable Scout source identity (for example, a fixed `scout_source_` prefix plus the source UUID without hyphens). `provider_kind` remains `ats`; `external_job_id` remains the ATS job identifier. This is a recommended contract, not yet implemented.

**Important distinction: the existing internal route is not a Scout intake endpoint**

`POST /api/internal/jobs/ingest` authenticates a cron/operator secret and calls Thungatha's own configured provider ingestion. It does not accept a Scout normalized-job batch. Scout must not call it expecting to push records. A dedicated authenticated intake route would need to be added to Thungatha if that transport is selected.

**Transport options for M8 — not implemented**

1. **Scout calls the existing destination RPCs server-to-server.** Scout would hold a separate Thungatha destination publishable/service credential in backend-only configuration and call the three RPCs through the Supabase REST interface. The destination service credential must never be confused with or stored as the Scout operational DB credential. This reuses the current controlled write contract and avoids changing Thungatha's API, but increases the impact of a compromised Scout backend credential.
2. **Add a dedicated Thungatha intake endpoint.** Scout sends a validated batch to a new authenticated server-to-server endpoint. Thungatha owns its destination credential and calls the same RPCs internally. This adds a second API contract and deployment dependency but keeps destination credentials inside Thungatha.

**Recommendation:** prefer the existing RPC path for the first implementation if the security review accepts a dedicated, least-privilege destination credential held only by Scout's backend. If credential isolation is judged more important than implementation simplicity, implement the dedicated intake endpoint instead. The final transport choice requires review before M8; neither path is authorised or implemented by this checkpoint.

**Failure and idempotency rules**
- Create/finish a destination ingestion run per stable source-specific provider key.
- Send only records that passed Scout's publication gates.
- Batch persistence must be retryable; the destination unique key prevents duplicate source records for the same provider key and external job ID.
- Preserve destination run state and sanitized error outcomes. Do not mark Scout records published until the destination confirms persistence.
- A failed/partial Scout extraction must not trigger destination unavailability or expiry reconciliation.
- Retry publication independently from extraction, using Scout's own publication ledger/idempotency state.
- Never send raw/rejected/exception records or Scout operational metadata to Thungatha.

**C04 outcome:** The actual destination schema, normalized JSON contract, controlled RPC functions, privileges and existing route behavior are documented. The transport choice and implementation remain deferred. No destination data was written and no publishing code was added.
