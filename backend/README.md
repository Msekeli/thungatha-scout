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

```bash
uvicorn scout.main:app --reload
```

Health check: `GET http://127.0.0.1:8000/health`.

The database URL is loaded as a secret setting. Database connectivity and
schema migrations are implemented in a later persistence checkpoint; this
configuration change does not yet open a database connection.
