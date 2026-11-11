# South African Careers-Page Crawling and ATS Adapter Strategy

**Status:** Proposed implementation baseline for review  
**Updated:** 11 November 2026  
**Branch:** `dev`

## 1. Decision and objective

Reprioritise source-platform investigation around employers and career sites relevant to the South African market. Do not assume the current international-first adapter sequence maximises South African employer coverage.

Greenhouse remains the proven reference adapter. Existing Greenhouse, Lever and Teamtailor work is retained; this decision does not delete or rewrite accepted integrations. Pause implementation of the remaining international-first M4 candidates until the South African investigation wave has been evaluated.

Platform names in this document are investigation candidates, not claims that every named employer currently uses that platform or that a public extraction method is available.

## 2. What the crawler is for

The crawler complements ATS adapters. It is not a replacement for them.

1. **Employer-first careers discovery:** find official employer careers pages for the target South African employer cohort, including branded/custom-domain pages that do not expose an obvious ATS hostname.
2. **Platform fingerprinting:** inspect redirects, canonical URLs, HTML, metadata, script references, structured data, embedded configuration and public network requests to identify the career-site platform with evidence.
3. **Source mapping:** discover job-listing routes, board/site identifiers, pagination patterns and vacancy-detail links. Save evidence and confidence; do not infer an adapter solely from a URL pattern.
4. **Non-standard careers extraction:** retrieve public HTML/JSON/RSS/XML career pages where no reliable supported ATS endpoint exists.
5. **Change detection:** periodically check known careers pages for platform changes, new vacancy links and source health.
6. **Adapter handoff:** when a known ATS is detected, hand the source URL/configuration to the matching adapter. The crawler must not duplicate that adapter's API/feed extraction.
7. **Coverage measurement:** report unique employers and verified career sources separately from platform detections, boards and vacancy counts.

The crawler must not crawl the whole web indiscriminately, search for personal data, bypass authentication/CAPTCHAs, evade rate limits, or ignore robots.txt and applicable site terms. Respect request budgets and identify Scout appropriately where practical.

## 3. Crawler execution model

Use Scrapy as the default HTTP crawling framework for public HTML and linked resources. Use Playwright only for pages where inspection proves browser execution is required; first inspect browser network traffic for a public JSON/API endpoint that can be called directly.

Scrapy Cloud (Zyte) is the candidate managed execution/scheduling environment obtained through the GitHub Student Developer Pack. Before relying on it, verify the current Pack offer, account eligibility, credit/usage limits, retention and scheduling availability. Do not assume unlimited or permanently free execution. Keep spiders runnable locally and keep deployment configuration portable so Scout is not locked to Scrapy Cloud.

The crawler should be a separately executable Scout worker, not a new microservice with its own database or a second ingestion pipeline.

### Runtime flow

```text
Employer cohort / official careers URL
              |
              v
       Scrapy discovery spider
              |
              v
  Redirect + page + platform evidence
              |
              v
   Source classification and routing
       /                    \
Known ATS adapter       Generic careers page
       |                    |
       v                    v
Existing adapter       Scrapy HTML/JSON parser
       \                    /
        v                  v
       Shared extraction contract
                  |
                  v
      Existing Scout persistence,
      normalization and quality gates
                  |
                  v
       Existing Thungatha publisher
```

The crawler submits observations to Scout's existing backend services. It must not write directly to Thungatha or create another database. Scout PostgreSQL remains the operational source of truth.

## 4. Crawl stages and data captured

### Stage A — employer seed

Input is an employer record and its official website/careers entry URL. Seeds can come from the existing employer registry, administrator input or a separately measured discovery list. Employer identity remains distinct from source/platform identity.

### Stage B — bounded discovery

Follow only relevant same-site careers links and explicitly linked external recruitment destinations. Apply per-domain depth, page-count, response-size, concurrency and timeout limits. Record redirects and canonical URLs. Avoid crawling unrelated corporate pages.

### Stage C — source fingerprint

Capture:
- requested, final and canonical URL;
- HTTP status, content type and retrieval timestamp;
- page title and employer branding hints;
- ATS/platform hostnames, script names and recognizable public endpoint patterns;
- structured job data (for example JobPosting JSON-LD);
- careers/job-listing links and discovered pagination controls;
- public API/feed requests observed during browser inspection;
- robots/terms review status and crawl outcome.

Do not persist full HTML by default. Store bounded diagnostic excerpts or hashes only where needed; redact secrets and personal data.

### Stage D — extraction strategy

Choose one route:
- known supported ATS: invoke its existing adapter;
- public feed/API with stable and permitted behavior: implement or extend a focused adapter;
- ordinary public HTML/JSON: use the generic careers-page crawler/parser;
- JavaScript-only page with no usable public endpoint: evaluate Playwright as an explicit, bounded exception;
- login wall, CAPTCHA, blocked or unclear permission: mark unsupported/blocked and stop.

### Stage E — shared pipeline

Every extracted vacancy must use the existing normalized vacancy contract, source-scoped identity, persistence, duplicate detection, quality gates, lifecycle rules and publication ledger. Preserve source URL and exact vacancy/application destinations. Failed or partial crawls must never imply that unseen vacancies have expired.

## 5. South African platform investigation priorities

Priorities below determine investigation order, not implementation commitments. Verify each employer's current official careers page and the live technical retrieval method before coding.

### Wave 1 — enterprise platforms and known South African employer leads

| Candidate platform | Employer leads to inspect | Current evidence status |
|---|---|---|
| SAP SuccessFactors | Sanlam; Capitec Bank | User-identified South African examples. Sanlam has historical/variable SuccessFactors evidence in the registry. Reconfirm both current career portals, redirects and actual vacancy requests. |
| Workday | Old Mutual; Pick n Pay; other major local employers discovered during research | Old Mutual mapping is present in the registry; Pick n Pay mapping is explicitly unverified. Verify each live site and vacancy endpoint. |
| Oracle Recruiting Cloud | South African enterprise employers identified from official careers pages | Candidate only until employer-specific official-page and network evidence is recorded. |
| Oracle Taleo | Legacy enterprise career portals discovered during employer research | Candidate for legacy compatibility; do not assume current adoption or prioritise over active platforms. |
| SmartRecruiters | South African employers identified from official careers pages | Candidate; establish actual local employer coverage first. |

### Wave 2 — locally relevant and mid-market platforms

| Candidate platform | Employer leads to inspect | Current evidence status |
|---|---|---|
| Simplify.hr | Media24; homechoice; other South African employer portals | Existing research records Media24 and homechoice as hosted career pages; verify live vacancy extraction behavior. |
| eRecruit | Shoprite Group; Boxer; CCBA; Clover | Existing registry records public eRecruit candidate portals. This identifies the portal technology, not Graylink Neptune. |
| BambooHR | South African employers found through official career-page discovery | Candidate; public job-board behavior and local employer coverage need verification. |
| Breezy HR | South African employers found through official career-page discovery | Candidate; public job-board behavior and local employer coverage need verification. |
| Workable | South African employers found through official career-page discovery | Candidate; inspect public board/widget behavior and exact job destinations. |

### Wave 3 — retain and extend where employer yield justifies it

Greenhouse, Lever, Teamtailor and Ashby remain in the adapter catalogue. Greenhouse is the reference implementation. Lever and Teamtailor already have implementation work recorded. Do not discard them; measure their verified South African employer yield before scheduling additional work.

Workday remains a valid enterprise candidate and should not be excluded merely because it was previously deferred. SAP SuccessFactors is promoted to the first investigation wave.

## 6. Investigation scorecard

For every employer/platform pair, record:
- employer name and official website;
- official careers entry URL and final URL after redirects;
- platform detection evidence and confidence;
- sample live vacancy URLs and count observed;
- public endpoint/feed and HTTP method;
- pagination/completeness behavior;
- detail/description retrieval;
- stable external ID;
- exact application destination;
- rate limits, robots/terms and other access constraints;
- extraction approach (existing adapter, new adapter, generic crawler, Playwright, blocked);
- unique South African employer coverage contribution;
- investigation date, evidence links and unresolved questions.

Rank platforms by verified unique direct-employer coverage, relevant South African vacancies, retrieval reliability, completeness and maintenance cost. Do not rank by global vendor popularity, number of boards found or raw vacancy count alone. Keep recruitment agencies/staffing firms separate from direct employers.

## 7. Delivery milestones

- **M1 — Employer and platform evidence:** build and maintain the employer-first South African careers-page cohort and evidence scorecard.
- **M4-SA-A — Crawler foundation and source fingerprinting:** prove Scrapy discovery against a small, diverse cohort; persist source observations through Scout's backend; test bounded crawling and failure semantics.
- **M4-SA-B — South African enterprise platform investigations:** investigate SAP SuccessFactors, Workday and Oracle Recruiting Cloud against named employer career pages. Produce evidence and technical designs before adapter implementation.
- **M4-SA-C — Local and mid-market platform investigations:** investigate Simplify.hr, eRecruit, BambooHR, Breezy HR and Workable.
- **M4-SA-D — Adapter implementation and integration:** implement only platforms with a permitted, reliable public retrieval method and meaningful verified employer coverage. Reuse the existing adapter contract and shared pipeline.
- **M6 — Held-out employer compatibility:** use a South African employer not used to implement the selected integration to test generic URL discovery, platform detection and source configuration without employer-specific code.

M4-SA checkpoints replace the previous planned Personio/Recruitee/Workable-first sequence. Existing accepted work and historical reports remain intact. The exact cohort and order can be adjusted from evidence, but no adapter is approved solely by appearing in this candidate list.

## 8. Acceptance criteria

- Scrapy can discover and fingerprint bounded public careers pages locally.
- A detected known ATS is routed to its existing adapter rather than scraped redundantly.
- Generic public career pages can yield structured vacancy observations with stable IDs or an explicit unresolved identity outcome.
- Crawl observations include provenance, completeness and failure classifications.
- The crawler uses Scout backend persistence and the existing quality/publication pipeline; no second database or direct Thungatha writes exist.
- Unit/contract tests cover redirects, robots/terms outcomes, pagination, duplicates, blocked pages, malformed data, timeouts, partial crawls and safe shutdown.
- Representative South African employer evidence demonstrates useful unique-employer coverage before platform adapter expansion proceeds.
- Scrapy Cloud eligibility, limits and costs are verified before scheduled hosted execution is enabled.
