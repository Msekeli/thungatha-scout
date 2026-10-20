# Thungatha Scout Backend

Python prototype for investigating employer careers pages and recording evidence for human review.

## Current status

- [x] Free-first web search prototype using the `ddgs` metasearch library.
- [x] Careers URL inspection and evidence-based ATS detection.
- [x] Greenhouse public-board API adapter.
- [x] Automated Greenhouse board discovery from public search results, with API validation and a separate timestamped registry.
- [x] Workday public CXS adapter using observed tenant/site configuration.
- [x] Generic same-host vacancy-detail extraction for ordinary careers pages.
- [x] Separate timestamped JSON and Markdown investigation reports.
- [ ] Validate extraction completeness and endpoint stability across more employer sites.
- [ ] Add Workday pagination and additional ATS adapters after tests justify them.
- [ ] Add the supplied employer URLs as a deduplicated benchmark dataset.
- [ ] Test JavaScript-rendered sites and add Playwright only if needed.

Search results are leads, not verified employers. Results can be incomplete or rate-limited, and employer type is heuristic. A careers page does not by itself prove that there are current vacancies.

## Setup

From the `backend` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Discover companies first (Cape Town / Western Cape)

Company discovery is deliberately separate from vacancy discovery. The default search finds technology employers and official company/careers web sources in Cape Town and the Western Cape; it does not search individual job titles. Results are candidate companies, not yet verified records, and should be reviewed for an official website and a valid careers URL before job extraction.

```bash
python -m app.main
python -m app.main discover --max-results-per-query 15
python -m app.main discover --region "Western Cape, South Africa" --max-results-per-query 15
python -m app.main discover --query '"technology companies in Cape Town" -recruitment -staffing'
```

Results are written to `company_discovery_results.csv`. Queries target vacancy and careers evidence across industries and search public ATS domains including Greenhouse, Lever, Workday, SmartRecruiters, Workable, Ashby, and Breezy HR. Search results may still be incomplete or ambiguous; retain the source URL and verify the actual employer and Cape Town/Western Cape connection before accepting a company into the registry. Existing `data/companies.csv` is not modified.

## Automatically discover Greenhouse boards

Run one command to search public web results for Greenhouse boards, validate candidate board tokens against the public Greenhouse API, and save evidence plus a separate CSV registry:

```bash
python -m app.main discover-greenhouse
```

Optional controls:

```bash
python -m app.main discover-greenhouse --max-results-per-query 30
python -m app.main discover-greenhouse --backend brave,google
```

Reports are saved under `reports/greenhouse-discovery/`. The JSON report retains search evidence and job records; the CSV registry contains only boards whose API returned usable, uniquely identified jobs. This does not modify `data/companies.csv`.

Discovery is automated but not exhaustive: coverage depends on public search indexing and search-provider rate limits. A validated public board confirms the feed is readable, not that every vacancy is relevant to a target region. Rerun the command periodically to find newly indexed boards.

## Rank discovered Greenhouse jobs for South Africa

Use the JSON report path printed by `discover-greenhouse`:

```bash
python -m app.main analyze-greenhouse reports/greenhouse-discovery/greenhouse-discovery-YYYYMMDDTHHMMSSZ.json
```

The command creates `reports/greenhouse-analysis/greenhouse-job-relevance.csv` and `greenhouse-job-relevance.json`. It ranks jobs using the available title, department, and location fields, flags South African locations, separately identifies remote roles whose eligible countries are unconfirmed, and keeps jobs with missing locations for manual review. It deduplicates exact vacancy URLs (ignoring trailing slashes). These are heuristic matches; open the original job page to confirm the vacancy is live and whether applicants in South Africa are eligible.

## Verify a known careers URL

```bash
python -m app.main verify https://careers.capitecbank.co.za/
```

## Investigate a careers URL

```bash
python -m app.main investigate https://ozow.com/jobs
python -m app.main investigate https://www.beingit.co.za/Careers
python -m app.main investigate https://www.relx.com/careers
```

The investigator:
- Records HTTP status, final URL, content type, response size, title, and a short text excerpt.
- Detects ATS platforms only when page HTML, configuration, or observed links provide evidence.
- Tries Greenhouse's public board API when the page exposes a board token.
- Follows an observed Workday careers link to inspect its public tenant/site configuration, then tries the public CXS jobs endpoint.
- For non-ATS pages, follows up to 25 observed same-host vacancy-detail links and extracts basic title and description evidence.
- Saves timestamped JSON and Markdown reports under `backend/reports/url-investigations/` by default.

To select another report directory:

```bash
python -m app.main investigate https://example.com/careers --output-dir /path/to/reports
```

ATS detection is not the same as successful extraction. Workday currently requests only the first page. Generic HTML extraction is intentionally conservative and may miss listings rendered only by JavaScript or links with unusual structures. Review the report rather than treating zero extracted jobs as proof that no vacancies exist.

The tool investigates only URLs you explicitly provide, does not edit `data/companies.csv`, does not access account-protected content, and never submits applications.

## Run tests

From the `backend` directory:

```bash
python -m pytest
```
