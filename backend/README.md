# Scout backend

FastAPI HTTP API and provider-portable processing code. Requires Python 3.11+.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn scout.main:app --reload
```

Health check: `GET http://127.0.0.1:8000/health`. No database or cloud resource is connected by this starter. Never commit `.env`.
