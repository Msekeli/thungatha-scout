# Scout backend

FastAPI HTTP API and provider-portable processing code. Requires Python 3.11+.

## Local setup

The API runs locally, but its operational database is the cloud-hosted Scout
Supabase PostgreSQL project. Do not install or run PostgreSQL locally.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env` and set:

- `SCOUT_DATABASE_URL` to the dedicated Scout Supabase Transaction Pooler URI.
Authentication is intentionally deferred during the initial functional
application build. Only the dedicated Scout database URL is required for the
current local registry workflow. Do not expose this unauthenticated development
API to the public internet. Authentication will be restored before deployment
or external access.

Keep passwords and keys in `.env`; never put real values in `.env.example`
or commit them. Do not use the Thungatha destination project's URL or keys here.

## Database migrations

Apply versioned SQL migrations to the Scout Supabase project:

```bash
python -m scout.persistence.migration_runner
```

The runner records migration versions and SHA-256 checksums in
`scout_schema_migrations`. Applied migrations are not rerun; editing an
already-applied migration is rejected. Add a new numbered SQL migration instead.

The connection uses Psycopg 3 with TLS, a bounded connection timeout, and
automatic prepared statements disabled for Supabase Transaction Pooler
compatibility.

## Tests

Run unit tests without touching the cloud database:

```bash
pytest test-suites/unit-tests
```

Cloud integration tests are opt-in because they create and remove temporary
test records in the Scout Supabase project:

```bash
SCOUT_RUN_DATABASE_INTEGRATION_TESTS=true pytest test-suites/integration-tests
```

The integration test applies pending migrations before testing employer/source
persistence. Do not enable it against the Thungatha destination project.

## Import the checked-in employer registry

The checked-in employer/source registry can be imported into the Scout database
without manually recreating each record:

```bash
python -m scout.registry_importer
```

The import is repeat-safe: existing employer names and normalized source URLs
are matched rather than duplicated. It imports supported Greenhouse and Workday
sources only. Other ATS/career-site types are reported as skipped until their
adapter is implemented.

Registry evidence is retained as claims, but imported employers remain
`discovered`, imported sources remain `discovered`, and source permission
remains `unknown`. A registry entry marked verified is not automatically
promoted to an approved database state. Confirm employer identity, Cape Town
presence, source relationship and permission through the admin review process.

## Registry API

The current local admin workflow exposes these endpoints without authentication
while the functional application is being built:

- `GET /api/v1/employers` — list employers (supports `limit` and `offset`).
- `POST /api/v1/employers` — register an employer.
- `GET /api/v1/employers/{id}` — read an employer.
- `GET /api/v1/employers/{id}/sources` — list its ATS sources.
- `POST /api/v1/employers/{id}/sources` — register a Greenhouse or Workday source; required adapter configuration is checked against the ATS registry.
- `GET /api/v1/greenhouse/inspect?url={board_url}` — inspect a Greenhouse board URL, retrieve board metadata and the complete public jobs response with descriptions.
- `POST /api/v1/sources/{source_id}/extract` — retrieve a registered Greenhouse source and upsert its vacancies into Scout.
- `GET /api/v1/vacancies` — list active vacancies across employers.
- `GET /api/v1/employers/{employer_id}/vacancies` — list active vacancies for one employer.

The Greenhouse Job Board API returns the public jobs collection with `meta.total`; Scout checks that count against the returned array. An incomplete response is recorded as partial and is never used to expire missing vacancies. Repeated extraction upserts by `(source_id, external_job_id)` rather than creating duplicates.

New employers and sources are stored as discovered; callers cannot set approval
or permission states. This API is for local development only until authentication
is reinstated.
## API

```bash
uvicorn scout.main:app --reload
```

Health check: `GET http://127.0.0.1:8000/health`.
