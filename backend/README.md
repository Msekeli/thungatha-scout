# Thungatha Scout Backend

Python prototype for discovering direct-employer careers sources and recording evidence for human review.

## Current status

- [x] Candidate model preserves source URLs and evidence.
- [x] Free-first web search prototype using the `ddgs` metasearch library.
- [x] Reusable HTTP/HTML inspection for a known careers URL.
- [x] URL investigation command with evidence-based ATS detection.
- [x] Greenhouse public-board API adapter and initial Workday public CXS adapter.
- [x] Separate JSON and Markdown investigation reports.
- [ ] Validate extraction completeness and endpoint stability across real employer sites.
- [ ] Add pagination and more ATS adapters only after test evidence supports them.
- [ ] Evaluate search quality and rate limits across several queries.
- [ ] Add the supplied employer URLs as a deduplicated benchmark dataset.
- [ ] Improve direct-employer and recruiter classification using verified evidence.
- [ ] Test JavaScript-rendered sites and add Playwright only if needed.

Search results are leads, not verified employers. Results can be incomplete or rate-limited, and employer type is heuristic. Manually review uncertain entries before adding them to a trusted directory. A careers page does not by itself prove that there are current vacancies.

## Setup

From the `backend` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Discover companies

Run the default queries for technology roles in Cape Town / Western Cape:

```bash
python -m app.main
```

Run one custom query:

```bash
python -m app.main discover --query '"software developer" careers "Cape Town" -recruitment'
```

Change search result limits:

```bash
python -m app.main discover --max-results-per-query 5
```

The results are written to `company_discovery_results.csv`.

## Verify a known careers URL

```bash
python -m app.main verify https://careers.capitecbank.co.za/
```

This command inspects a known URL; it does not discover new employers.

## Investigate a careers URL (recommended for experiments)

Run one investigation for a URL you supply:

```bash
python -m app.main investigate https://ozow.com/jobs
```

For RELX, supply the corporate careers URL; the investigator follows an observed Workday link to read its public tenant/site configuration:

```bash
python -m app.main investigate https://www.relx.com/careers
```

The command automatically:
- Fetches the supplied page and records HTTP status, final URL, content type, response size, title, and a short text excerpt.
- Detects ATS platforms only when page HTML, configuration, or links provide evidence.
- Tries the Greenhouse public-board API when a board token is found in the supplied page.
- Tries the public Workday CXS jobs endpoint when an observed Workday URL and tenant/site configuration are available.
- Saves timestamped JSON and Markdown reports under `backend/reports/url-investigations/` by default.

You can choose another report directory with `--output-dir /path/to/reports`.

Important: ATS detection is not the same as successful extraction. Reports distinguish adapter success, HTTP status, returned job count, and errors. Workday currently requests only the first page of jobs. Unsupported platforms are reported without blind endpoint probing; browser automation has not been added. This tool only investigates URLs you explicitly provide, does not edit `data/companies.csv`, and never submits applications.

## Run tests

From the `backend` directory:

```bash
pytest
```
