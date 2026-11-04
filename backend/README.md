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
- `SCOUT_SUPABASE_URL` to the same Scout Supabase project URL.
- `SCOUT_SUPABASE_PUBLISHABLE_KEY` to that project's publishable key.
- `SCOUT_ADMIN_EMAIL` to the single administrator email allowed to use Scout.

Keep passwords and keys in `.env`; never put real values in `.env.example`
or commit them. Do not use the Thungatha destination project's URL or keys here.
The publishable key is not a service-role key. In the Scout Supabase Auth
settings, disable public sign-ups and require email confirmation for the
configured administrator account. The backend allowlist remains mandatory
even when those dashboard controls are enabled.

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

## API authentication

Protected FastAPI routes must declare the `require_admin` dependency from
`scout.authentication`. It verifies Supabase user access tokens and enforces
the configured administrator email. The health route is intentionally public.
Do not expose service-role credentials to the browser.

Asymmetric ES256/RS256 tokens are verified against Supabase JWKS. Legacy HS256
tokens are validated by the Supabase Auth user endpoint. The latter requires
the publishable key and a bounded Auth request.

## API

```bash
uvicorn scout.main:app --reload
```

Health check: `GET http://127.0.0.1:8000/health`.
