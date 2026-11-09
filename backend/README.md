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

Edit `.env` and set `SCOUT_DATABASE_URL` to the dedicated Scout Supabase
Transaction Pooler URI. Never use the Thungatha destination project's URL or
keys in Scout.

Keep passwords and keys in `.env`; never put real values in `.env.example`
or commit them. The local development API permits the export endpoint without
a machine key only when `APP_ENV=development` or `APP_ENV=test`. Do not expose
that development configuration to the public internet.

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

Apply pending database migrations before importing the employer registry:

```bash
python -m scout.persistence.migration_runner
python -m scout.registry_importer
```

The importer reads `registry/employer-source-registry.json` and supports the
implemented Greenhouse, Lever and Workday adapters. Unsupported source adapters
are skipped and reported. The import is repeat-safe: existing employer names
and normalized source URLs are matched rather than duplicated.

Registry evidence is retained as claims. Imported employers and sources remain
`discovered`, and source permission remains `unknown`. A registry entry
marked verified is not automatically promoted to an approved database state.
Confirm employer identity, Cape Town presence, source relationship and
permission through the admin review process.

## Vacancy export API

Scout exposes a read-only vacancy export for server-side consumers such as
Thungatha:

- `GET /api/v1/vacancies/export`
- Query parameters: `limit` (1–100, default 50), `offset` (default 0), and
  `location_scope` (default `south_africa`; options: `cape_town`,
  `western_cape`, `south_africa`, `all`).
- Only active, non-archived vacancies are returned. The endpoint does not run
  Greenhouse extraction or modify Scout records.
- Results are ordered by original publication date, source update date,
  creation date and immutable Scout vacancy UUID for stable pagination.
- Descriptions are returned as sanitized HTML.
- `published_at` is the original employer publication date;
  `source_updated_at` is the latest employer-reported update date; and
  `first_seen_at` is when Scout first discovered the vacancy. Missing source
  dates remain null; discovery time is never substituted for publication time.
- The export intentionally exposes Scout's contract, not Thungatha's database
  schema. It omits raw ATS payloads and source-specific internal identifiers.

The JSON response contains `items`, `total`, `limit`, `offset`, `has_more`
and `location_scope`. Each item contains `scout_vacancy_id`,
`employer_name`, `logo_url`, `title`, `description`, `location_text`,
`application_url`, `published_at`, `source_updated_at` and
`first_seen_at`.

Example local request:

```bash
curl "http://127.0.0.1:8000/api/v1/vacancies/export?limit=50&offset=0"
```

For server-to-server access, set a long random `SCOUT_EXPORT_API_KEY` in
Scout's server environment and send the same secret from Thungatha in the
`X-Scout-Export-Key` header. Once configured, the key is required in every
environment. In production, the endpoint fails closed with HTTP 503 if the
key is not configured; missing or incorrect keys receive HTTP 401. Never put
this key in browser code or commit it.

Example production request:

```bash
curl "https://YOUR_SCOUT_API_HOST/api/v1/vacancies/export?limit=50&offset=0" \
  -H "X-Scout-Export-Key: YOUR_SERVER_SIDE_EXPORT_KEY"
```

Thungatha must call this endpoint from its server-side code, validate the
response, map Scout fields to its own model and persist records in the
Thungatha database. Scout never connects to the Thungatha database.

## API

```bash
uvicorn scout.main:app --reload
```

Health check: `GET http://127.0.0.1:8000/health`.
