# Thungatha Scout

Thungatha Scout is a company-first discovery tool for finding direct employers that hire software developers and related technology roles, initially focused on Cape Town and the Western Cape.

## Initial goal

Automate the early research process:

1. Discover potential direct employers from public sources.
2. Separate direct employers from recruitment agencies, job boards, and uncertain results.
3. identify and inspect official company and careers pages.
4. Record evidence and source URLs so results can be reviewed.
5. Keep employer discovery distinct from vacancy extraction and job publication.

## Current milestone

The first milestone is a local Python proof of concept to test company discovery using free-first sources and verify discovered careers URLs. A list of manually supplied URLs is useful as a benchmark, but is not the discovery mechanism itself.

No AI provider, paid search API, database, frontend, scheduled job, or integration with Thungatha is required for this first milestone.

## Project layout

```text
thungatha-scout/
├── frontend/           # Planned dashboard; not part of the current milestone
├── backend/
│   ├── app/            # Python application
│   ├── tests/           # Automated tests
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

## Current prototype dependencies

- Python 3.14 (local development)
- httpx
- Beautiful Soup 4

Playwright can be added only when tests show that JavaScript-rendered pages prevent reliable inspection.

## Run locally

From the `backend` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Principles

- Prefer free approaches and avoid unnecessary paid services.
- Treat search results as leads, not authoritative evidence.
- Prioritize direct employers; do not mix recruitment agencies into the direct-employer directory.
- Preserve evidence and URLs for review.
- Never infer that a company is hiring solely because it has a careers page.
- Keep human review available for uncertain employer or source classifications.
- Do not write to the Thungatha application or publish jobs during this milestone.


## Automated Greenhouse discovery

From `backend/` with the virtual environment active:

```bash
python -m app.main discover-greenhouse
python -m app.main discover-greenhouse --max-results-per-query 30
python -m app.main discover-greenhouse --backend brave,google
```

The command searches several query families for public Greenhouse board URLs and
company careers pages, then inspects a bounded number of those pages for explicit
Greenhouse API or embed references. Each discovered token is checked against
Greenhouse's public jobs API. The JSON report preserves search evidence and
validation errors; the CSV registry includes only boards whose feeds contain
usable, uniquely identified jobs. Reports are saved under
`backend/reports/greenhouse-discovery/` by default.

This is broader discovery, not an exhaustive customer directory: search indexing
and rate limits constrain coverage. It does not guess board tokens from company
names, alter `companies.csv`, bypass access controls, or publish jobs into
Thungatha. Inspect the report's `company_pages_inspected`,
`company_page_errors`, and query counts when assessing coverage.
