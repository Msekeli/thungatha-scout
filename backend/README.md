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

Edit `.env` and set `SCOUT_DATABASE_URL` to the Supabase Transaction Pooler
connection string. Keep the real password in `.env`; never put it in
`.env.example` or commit it.

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

## API

```bash
uvicorn scout.main:app --reload
```

Health check: `GET http://127.0.0.1:8000/health`.
