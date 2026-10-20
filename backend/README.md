# Thungatha Scout Backend

Python prototype for discovering direct-employer careers sources and recording evidence for human review.

## Current status

- [x] Candidate model preserves source URLs and evidence.
- [x] Free-first web search prototype using the `ddgs` metasearch library.
- [x] Reusable HTTP/HTML inspection for a known careers URL.
- [x] CSV exports for discovered candidates and URL verification.
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
