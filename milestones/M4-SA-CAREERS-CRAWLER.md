# South African Careers Crawler and Platform Coverage

**Status:** In progress — M4-SA-A implementation started  
**Updated:** 13 November 2026  
**Branch:** dev

## Objective

Use Crawlee for bounded discovery of official careers pages, evidence-based ATS fingerprinting and reusable generic extraction. Preserve existing ATS adapters and the shared Scout ingestion/persistence pipeline.

## Architecture boundaries

- Crawlee is a library in the Scout worker, not a new microservice.
- HTTP-first crawling is the default. Playwright is a bounded fallback only after evidence shows it is necessary.
- Respect robots.txt, site terms, access controls and rate limits. Never bypass login walls, CAPTCHAs or blocks.
- Known ATS platforms route to existing registered adapters; do not retrieve the same board twice.
- Generic extraction is limited to public non-standard careers pages.
- All vacancy candidates must use the existing normalized contract and Scout persistence path.
- No second database, direct Thungatha writes or new hosted runtime.
- AI enrichment remains optional and outside this checkpoint.

## M4-SA-A — Crawlee foundation and source fingerprinting

**Status:** Implementation started; not accepted.

### Current implementation

- Added a Crawlee ParselCrawler execution boundary with configured request count, depth, concurrency, request timeout, one retry and robots.txt enforcement.
- Added source observations containing requested/final/canonical URLs, HTTP status, content type, title, detected platform, discovered links, vacancy candidates and observation time.
- Added host-based fingerprints for the existing Greenhouse, Lever, Workday, Workable and Teamtailor adapters. A detected ATS stops generic link crawling.
- Added deterministic JSON-LD JobPosting parsing into the existing NormalizedVacancy contract.
- Added fixture-based tests for known/unknown ATS hosts, malformed JSON-LD, normal postings and graph postings.

### Known gaps before acceptance

- The crawler currently returns observations in memory. It is not yet connected to an existing persistence record because Scout has no dedicated career-page observation repository/table. Do not add a second database or silently persist HTML.
- ATS fingerprint results are exposed to the caller; explicit dispatch through the registered adapter factories is still to be connected.
- The configured response-byte ceiling is currently checked after Parsel has parsed the response. This is not yet a transport-level download limit and must be tightened before production use.
- Failure/robots outcomes, redirects, same-host scope and partial crawl behavior still need mocked tests and live verification.
- No generic extraction result is yet persisted or published. Existing vacancy lifecycle and publication gates remain untouched.

### Verification

Not run in this checkpoint. The user requested implementation to proceed without running tests or UI checks unless explicitly asked. Do not treat generated tests as passing evidence.

## M4-SA-E — Zyte worker packaging and deployment

**Status:** Blocked until M4-SA-A is locally verified and accepted.

Use only the approved GitHub Student Developer Pack free unit. No paid units, Zyte API usage, upgrades or other paid infrastructure are approved. Manual deployment smoke test and user review are required before recurring scheduling.

## AI provider foundation

**Status:** Configuration only; provider implementation is not part of M4-SA-A.

Gemini and Groq remain optional interchangeable providers. Keep AI disabled by default and use deterministic extraction first.