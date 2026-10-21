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

Run one command to discover Greenhouse employer leads across industries and save an evidence-first company registry. The discovery stage does not filter by job title and does not require a board to have current vacancies:

```bash
python -m app.main discover-greenhouse
```

Optional controls:

```bash
python -m app.main discover-greenhouse --max-results-per-query 30
python -m app.main discover-greenhouse --backend bing
```

Reports are saved under `reports/greenhouse-discovery/`. The JSON report retains search evidence, board/API checks, candidate company names, page titles, source URLs, and any returned jobs as supporting evidence. The CSV keeps **all discovered board leads**, including unresolved identities, API failures, and boards with zero current jobs. This does not modify `data/companies.csv`.

Greenhouse discovery defaults to the single `bing` search backend. In this environment, diagnostic tests showed that `brave` and `google` returned no results while `bing` returned results. If Bing is unavailable, try `--backend auto` or another single backend. The default searches cover **Cape Town, the wider Western Cape, and Stellenbosch**, and do not restrict discovery to technology employers or specific roles. The report separates three questions: whether a Greenhouse reference was found, whether the public board API is accessible, and whether the employer identity is established. A board token is never treated as the company name. Names inferred from search or board-page titles remain candidates until checked against an employer's official website or careers page. Company-page HTML containing an explicit Greenhouse reference is retained as evidence, but it is not silently treated as proof that the page is official.

A public board/API is evidence of a Greenhouse board endpoint, not proof that the employer operates in the Western Cape. Confirm regional presence from official company/careers information before promoting a lead to the verified-company list. Search coverage is not exhaustive and depends on public indexing and provider availability. Vacancy analysis is a separate downstream stage; an empty job feed does not remove a company lead.

## Export all captured Greenhouse jobs (no role filter)

The discovery JSON already contains the public jobs returned by each board API. Export every captured vacancy—across all industries and job titles—without running discovery again:

```bash
python -m app.main extract-greenhouse-jobs reports/greenhouse-discovery/greenhouse-discovery-YYYYMMDDTHHMMSSZ.json
```

This creates `reports/greenhouse-jobs/greenhouse-jobs.csv` and `greenhouse-jobs.json`. Each job retains its company/board provenance, title, location, department, vacancy URL, description-availability flag, and extraction timestamp. The export deduplicates repeated vacancy URLs and adds simple Western Cape and South Africa location flags. It retains unresolved company identities and jobs outside the region; those flags are clues for filtering, not proof of applicant eligibility. This command exports the saved report only—it does not refresh live board APIs.

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
