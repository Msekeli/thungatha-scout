# South African Careers-Page Crawling and ATS Adapter Strategy

**Status:** Approved architecture direction; implementation pending checkpoint evidence  
**Updated:** 12 November 2026  
**Branch:** `dev`

## 1. Objective and decision

Use **Crawlee for Python** as Scout's reusable, bounded careers-page crawling framework. Crawlee complements ATS adapters; it does not replace them. Greenhouse remains the proven reference adapter. Existing Greenhouse, Lever and Teamtailor work is preserved.

The crawler discovers official employer careers pages, inspects redirects and linked pages, fingerprints platforms, and extracts public vacancies only when no supported ATS adapter is available. It is not a general-purpose whole-web crawler.

## 2. Responsibilities and boundaries

1. Discover relevant careers links from an employer's official website and configured seed URLs.
2. Follow bounded, relevant links and record requested, final and canonical URLs.
3. Fingerprint ATS/platform evidence from hostnames, redirects, metadata, structured data, scripts, embeds and public endpoint patterns.
4. Route known platforms to their existing registered ATS adapters.
5. Use generic HTML/JSON/feed extraction only for public career pages without a suitable adapter.
6. Produce source observations, crawl outcomes and vacancy candidates for Scout's existing application pipeline.
7. Measure unique employers, verified sources, platform detections and vacancies as separate metrics.

Crawlee must not create a second ingestion pipeline, database, or direct Thungatha writer. It must not approve employers/sources, bypass deterministic quality gates, or make publication decisions.

## 3. Crawlee execution strategy

Use Crawlee's HTTP-oriented crawler first for ordinary public pages. This is the low-cost, low-overhead path and should handle redirects, HTML/JSON retrieval, link discovery and platform fingerprints.

Use Crawlee's Playwright integration only when investigation shows that browser execution is necessary. Before enabling browser fallback, inspect public network requests and prefer a stable, permitted JSON/feed endpoint where available. Browser concurrency, page count, execution time and response size must be tightly bounded.

Crawlee is a library executed by Scout's own worker. It is not a commitment to Apify hosting or any paid managed platform. Local execution remains supported; hosting and scheduling remain deferred until workload verification and explicit cost review.

## 4. Runtime flow

```text
Official employer website / careers URL
                 |
                 v
       Crawlee bounded discovery
                 |
                 v
 Redirects, links and platform evidence
                 |
                 v
        Source classification
          /             \
   Known ATS          Generic page
      |                    |
      v                    v
Existing ATS adapter   Generic public parser
      \                    /
       v                  v
      Shared normalized vacancy contract
                    |
                    v
        Existing Scout persistence,
        quality/lifecycle and exception rules
                    |
                    v
          Existing Thungatha publisher
```

## 5. Crawl stages and evidence

### Seed and scope

Seeds come from configured employer careers URLs, administrator input or the approved discovery workflow. Employer identity and source identity remain separate. Restrict crawling to relevant same-site careers paths and explicitly linked recruitment destinations.

### Bounded retrieval

Configure maximum concurrency, requests per run, link depth, per-request timeout and maximum response bytes. Respect robots.txt, terms, access controls and rate limits. Do not bypass authentication, CAPTCHAs, blocks or technical restrictions. Apply bounded retries and backoff; classify failures rather than hiding them.

### Source fingerprint

Record requested/final/canonical URLs, status, content type, retrieval time, page title, platform clues, structured JobPosting data, careers/job links, observed public feed/API patterns, robots outcome and completeness. Preserve evidence references and confidence; a hostname or script match alone is not proof of employer ownership or source permission.

### Extraction routing

- Known configured ATS: existing adapter only; never scrape the same board again through the generic parser.
- Stable, public, permitted feed/API without an existing adapter: investigate a focused adapter using the shared contract.
- Public non-standard HTML/JSON page: generic parser and shared vacancy contract.
- JavaScript-only page: inspect network traffic first; use bounded Playwright only if no suitable public endpoint exists.
- Login wall, CAPTCHA, prohibited or unclear access: stop and record blocked/unsupported.

### Persistence and lifecycle

Crawl observations and vacancies flow through Scout's existing services and PostgreSQL repositories. Preserve source provenance, stable source-scoped identity and exact application destinations. Partial/failed crawls never imply vacancy removal or expiry. Do not retain full HTML snapshots by default; keep only bounded evidence required for diagnostics.

## 6. AI enrichment boundary

Gemini and Groq are interchangeable providers behind one small application-level interface. Deterministic parsing runs first. Invoke AI only for difficult description structuring or genuinely ambiguous extraction/classification, not for routine pages that deterministic rules can handle.

Use one configured primary provider and optionally fail over to the other on retryable provider failures. Do not call both providers for every record. Cache validated results by normalized input/content hash and prompt/schema version. Bound input characters, output tokens, timeout and retries. Validate every response against a strict schema; malformed, low-confidence or incomplete output falls back to original source content and/or the exception workflow.

AI cannot invent vacancy facts, establish source permission, approve employers, alter stable identity, override quality gates, set lifecycle state or publish. Record provider/model and validation outcome without logging API keys or unnecessary personal data. AI enrichment is opt-in and must remain usable with both providers disabled or unavailable.

## 7. South African investigation priorities

These are research candidates, not verified integrations or claims of current employer adoption.

**Enterprise wave:** SAP SuccessFactors (Sanlam and Capitec leads), Workday (including Old Mutual and verified additional employers), Oracle Recruiting Cloud, Oracle Taleo and SmartRecruiters.

**Local/mid-market wave:** Simplify.hr (Media24, homechoice), eRecruit (Shoprite Group, Boxer, CCBA, Clover), BambooHR, Breezy HR and Workable. Do not conflate eRecruit with Graylink Neptune.

**Retain and measure:** Greenhouse, Lever, Teamtailor and Ashby. Greenhouse remains the reference; existing Lever and Teamtailor work is retained. Prioritise by verified unique South African direct-employer coverage, completeness, reliability, permitted access and maintenance cost—not vendor popularity or raw vacancy count.

For each employer/platform pair record the official careers URL, final URL, fingerprint evidence, confidence, sample vacancies, public endpoint, pagination/completeness, stable ID, description, application URL, restrictions, retrieval approach, date and unresolved questions.

## 8. Delivery plan and acceptance

- **M4-SA-A — Crawlee foundation and source fingerprinting:** dependency/configuration, bounded HTTP discovery, redirect/link extraction, evidence contract, known-ATS routing, generic public-page observation, persistence handoff and deterministic tests.
- **M4-SA-B — Enterprise investigation:** SAP SuccessFactors, Workday and Oracle Recruiting Cloud against named official employer career pages; evidence and designs before adapter code.
- **M4-SA-C — Local/mid-market investigation:** Simplify.hr, eRecruit, BambooHR, Breezy HR and Workable.
- **M4-SA-D — Evidence-ranked integration:** implement only platforms with reliable, permitted public retrieval and useful verified employer coverage.
- **AI-ENRICHMENT — Provider foundation:** settings, secret handling, provider interface, Gemini/Groq implementations, structured validation, cache contract, failover and mocked tests. AI stays disabled until credentials and models are configured locally.

M4-SA-A acceptance requires bounded local crawling, explicit outcomes and provenance, known ATS handoff without duplicate retrieval, generic-page fixture coverage, shared persistence/pipeline integration, safe partial-run semantics, and mandatory repository quality checks. Live employer evidence is a separately recorded smoke test. No hosted recurring workload or paid usage is enabled by this plan.
