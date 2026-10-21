# Thungatha Scout

Thungatha Scout is a lightweight job-source feeder for Thungatha. It uses a curated registry of known employers and reusable adapters for their public careers platforms. Company discovery is deliberately out of scope for this milestone.

## Current milestone: validate Workday ingestion

The first adapter targets public Workday careers boards. Workday pages use a different public JSON request pattern from Greenhouse, so the integration must handle its own URL parsing, POST requests, pagination, and optional per-vacancy detail calls.

Test against Betway's public careers board:

```text
https://myhcm.wd3.myworkdayjobs.com/Betway_Africa
```

From `backend/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main workday "https://myhcm.wd3.myworkdayjobs.com/Betway_Africa" --max-jobs 40
```

Fetch full descriptions and additional detail fields only when needed:

```bash
python -m app.main workday "https://myhcm.wd3.myworkdayjobs.com/Betway_Africa" --max-jobs 20 --details --output /tmp/betway-workday.json
```

Workday's public CXS job-list endpoint uses POST requests with a page size of 20. The adapter preserves the initial total, increments the offset by 20, and also stops on an empty page. It does not interpret HTTP 403/429 or malformed responses as evidence that the employer has no vacancies. Detail requests are optional because they add one request per job.

The public CXS interface is undocumented and unsupported by Workday. Handle timeouts, schema changes, and rate limits; do not attempt to bypass access restrictions.

## Tests

Run from `backend/`:

```bash
python -m pytest
```

The Workday tests use mocked HTTP responses, so they verify URL parsing, page-size limits, pagination, normalization, and failure handling without relying on a live third-party site.

## Planned architecture

- Python Azure Functions app for manual and scheduled processing.
- Azure Functions Timer Trigger for a 12-hour refresh cadence.
- Azure Table Storage for employer sources, vacancy state, approvals, and publication outcomes.
- Next.js admin dashboard for reviewing candidates.
- Authenticated Thungatha publication API; only explicitly approved vacancies may be published.

These components are planned, not implemented in this initial adapter milestone. Blob Storage is optional and should be introduced only if larger evidence snapshots are needed.

## Design principles

- Maintain known employers and official careers URLs; do not run company discovery in the feeder.
- Use one adapter per recruitment platform, reusable across registered employers.
- Keep source IDs, canonical posting URLs, location and provenance fields for deduplication and review.
- Treat missing or failed source responses as errors, not as an empty vacancy list.
- Never publish a vacancy without explicit approval.
- Keep the implementation small and compatible with Azure Functions.
