# Thungatha Scout

Thungatha Scout is the employer-source and vacancy-ingestion component that supplies trusted listings to Thungatha.

## Scope

- Discover employers across industries and company sizes in **Cape Town**.
- Verify company identity and official careers sources before routine ingestion.
- Extract vacancies through replaceable career-site/ATS adapters.
- Normalize and deduplicate vacancy records while retaining source evidence and freshness.
- Require explicit human approval before publishing approved records to Thungatha.
- Make processing runs, review queues and failures visible to the protected admin UI.

An employer's official careers publication is the source authority. An ATS is an access mechanism, not proof of employer identity. Aggregator-only listings are not sufficient source evidence.

## Architecture

One **Azure Functions Python v2 Function App** hosts a small number of trigger functions. It is one deployable backend, not one function for the entire system and not a separate app per responsibility.

Planned trigger responsibilities:

1. Company discovery — weekly initially.
2. Company/source verification — weekly, with targeted rechecks.
3. Vacancy extraction — every 8 hours.
4. Publishing — after successful batches, plus scheduled recovery.
5. Protected admin HTTP operations — review queues, run status and review decisions.

The trigger functions should orchestrate small, ordinary Python modules. Do not create empty placeholder modules for every future feature; add modules when their contracts and behavior are ready.

## Data boundary

- **Azure Table Storage** holds Scout's internal candidates, companies, recruitment sources, vacancies and processing state.
- **Supabase** holds approved Thungatha-facing companies and vacancies, published through stable IDs and idempotent upserts.

Table Storage is not relational. Choose partition and row keys from actual access patterns. Keep privileged credentials server-side. Temporary source failures must not be interpreted as vacancies being closed, and AI must never approve or publish records autonomously.

## Backend development

The backend is in `backend/` and uses Azure Functions Python v2. Use a Python version supported by the selected Azure Functions runtime and hosting plan; verify compatibility before pinning versions or deploying.

Local setup (after installing a compatible Python runtime and Azure Functions Core Tools):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
func start
```

Copy `local.settings.json.example` to `local.settings.json` for local settings. Never commit real credentials or `local.settings.json`.

## Working principles

- Preserve Greenhouse experiments, Workday research, reports and historical company/source evidence on their research branches.
- Keep `dev` for the clean implementation baseline; do not copy research artifacts into it without review.
- Add adapters only when justified by verified sources and research evidence.
- Use bounded timeouts/retries and record run outcomes and source errors.
- Keep role relevance, geographic eligibility, source verification and vacancy freshness as distinct decisions.
- Run tests and quality checks before claiming a change works; record only commands actually run.

See `AGENTS.md`, `IMPLEMENTATION-PLAN.md`, `milestones/`, `AI-WORKING-GUIDE.md` and `CODING-STANDARDS.md` for working rules and delivery checkpoints. The source-of-truth document remains authoritative for established decisions and historical observations.
