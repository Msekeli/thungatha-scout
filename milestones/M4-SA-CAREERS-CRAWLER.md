# M4-SA — Crawlee Careers Discovery and Platform Coverage

**Status:** In progress — M4-SA-A implementation started  
**Updated:** 13 November 2026  
**Branch:** `dev`  
**Architecture decision:** Crawlee for Python; Gemini and Groq as optional AI providers

## Objective

Improve verified South African employer coverage through bounded discovery of official careers pages, evidence-based ATS fingerprinting and reusable generic extraction. Preserve the existing ATS adapter contract and shared Scout ingestion pipeline.

This milestone does not approve a new employer/source or bypass source restrictions. The user has approved the GitHub Student Developer Pack's Zyte Scrapy Cloud unit for the crawler worker only; deployment is gated by M4-SA-E and must not incur paid charges.

## Required reading

Read `AGENTS.md`, `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`, `IMPLEMENTATION-PLAN.md`, `TECHNICAL-APPROACH.md`, `AI-WORKING-GUIDE.md`, `CODING-STANDARDS.md`, `docs/CAREER-PAGE-CRAWLER-IMPLEMENTATION.md`, both ATS/employer registries, and the existing extraction service/contracts before implementation.

## Architecture boundaries

- Crawlee is a library in the Scout worker, not a new microservice.
- HTTP-first crawling is the default. Playwright is an explicit, bounded fallback after evidence shows it is necessary.
- Respect robots.txt, site terms, access controls and rate limits. Do not bypass login walls, CAPTCHAs or blocks.
- Known ATS platforms route to their existing registered adapter. Do not retrieve the same board twice.
- Generic extraction handles public non-standard careers pages only.
- All observations and vacancy candidates flow through existing Scout services, persistence, normalized contracts, quality/lifecycle checks, exceptions and publication ledger.
- No second database, direct Thungatha writes or new hosted runtime.
- AI enrichment is optional. Deterministic parsing runs first; Gemini/Groq cannot approve, invent evidence, override gates or publish.

## Checkpoints

### M4-SA-A — Crawlee foundation and source fingerprinting

**Status:** Implementation started; not accepted.

1. Inspect the current repository, worker entry points, extraction service, adapter contracts, persistence and registries. Do not duplicate existing responsibilities.
2. Implement a small Crawlee execution boundary with bounded request/depth/domain scope, concurrency, response bytes, timeout, retry and graceful shutdown settings.
3. Capture requested/final/canonical URLs, status, content type, timestamps, relevant links, platform evidence, robots outcome, completeness and explicit failure classification.
4. Route known ATS fingerprints to existing adapters without generic duplicate retrieval.
5. Parse only public non-standard pages through a generic observation/extraction contract.
6. Persist observations through existing Scout repositories/services; do not retain full HTML by default.
7. Add deterministic fixtures and mocked tests for redirects, link scope, fingerprints, robots/blocked outcomes, malformed responses, timeouts, partial crawls and duplicate routing.
8. Verify partial/failed crawls cannot mark vacancies removed or expired.
9. Run focused tests and mandatory repository line-limit/naming checks.

**Acceptance:** local bounded crawler works; provenance and completeness are recorded; known ATS routing is tested; generic page observations enter the shared pipeline; failures are explicit and safe. Live employer smoke tests are recorded separately.\n**Implementation progress (13 November 2026):**

- Implemented Crawlee's HTTP crawler with request/depth/concurrency/time limits, bounded streaming response reads, one retry, robots.txt enforcement and blocked-request bypass disabled.
- Added URL, status, content type, title, canonical URL, platform, observation time, discovered-link and vacancy-count evidence. Observations are stored in the existing employer-source discovery preview; HTML bodies are not retained.
- Added fingerprints for Greenhouse, Lever, Workday, Workable and Teamtailor, plus routing to a matching already-registered ATS source. Generic extraction runs only when no registered ATS source matches.
- Added a generic `career_page` source type using the existing employer source table, extraction runs, normalized vacancy contract and vacancy repository. Migration `0016` adds the source type.
- Generic JSON-LD vacancies without a location are withheld and make the run partial; partial/failed runs do not expire missing vacancies.
- Added fixture tests for platform fingerprints, JSON-LD mapping and generic source configuration. Tests have not been run.

**Still open before acceptance:**

- Verify redirect safety, same-site/external ATS link boundaries, robots skip outcomes, malformed/empty responses, timeout behavior and duplicate routing with mocked tests.
- Confirm the existing source registration UI accepts the new `career_page` source configuration end to end.
- Review the existing Cape Town-only source-of-truth versus the current South Africa-wide ingestion gate before accepting generic vacancy coverage. No geography policy was changed here.
- Run focused tests and mandatory line-limit/naming checks locally. Live employer smoke tests remain separate.

## Branding follow-up after M4-SA-A

Crawlee is not responsible for employer logo discovery or replacement. After M4-SA-A is completed and reviewed, revisit the existing deterministic employer-branding implementation. Preserve working official logos, repair provenance and frontend validation issues, and use discovery only as a fallback when the official logo is genuinely difficult to locate. Never use an ATS vendor favicon as the employer logo.

### M4-SA-E — Zyte Scrapy Cloud worker packaging and deployment

**Status:** Approved target; blocked until M4-SA-A produces a working local worker.

1. Add the minimal Scrapy project metadata required by Zyte Cloud and declare a standalone Python worker entry script in `setup.py`. Do not implement crawler behavior in Scrapy.
2. Keep Crawlee and the existing Scout services/persistence as the runtime and business-logic owners. The Zyte wrapper only starts the existing worker.
3. Confirm the supported Zyte stack can install the pinned Crawlee/Playwright dependencies. Use Playwright only if the one-unit runtime and memory budget support the required browser fallback; otherwise keep browser fallback disabled in cloud jobs until measured.
4. Configure the Scrapy Cloud project ID and deployment credentials outside source control. Use the Scrapy Cloud API key for `shub`, not a Zyte API key. Keep Scout database and AI provider credentials in protected job/project environment settings; never commit them.
5. Deploy to the existing user-created Zyte project and run one manually triggered, bounded smoke job. Confirm the worker reaches the existing Scout ingestion services and writes only to the Scout database.
6. Verify one-hour hard timeout, non-overlap, single-unit memory constraints, graceful shutdown, sanitized logs, explicit success/partial/failed outcomes and recovery behavior.
7. Configure the approved 06:00 and 18:00 `Africa/Johannesburg` schedule only after the manual job and user review pass. Ensure failed/partial runs cannot expire vacancies.
8. Record actual deployment/job IDs, runtime, resource use and acceptance evidence. Do not claim cloud deployment until a real job completes successfully.

**Acceptance:** a deployed Crawlee worker runs as a standalone Python script in Zyte Scrapy Cloud without porting crawling to Scrapy; persists through the existing Scout pipeline; respects all source and execution limits; and has an accepted manual smoke run before recurring scheduling.

**Cost boundary:** use only the user's GitHub Student Developer Pack free unit. No paid units, upgrades, Zyte API usage or other paid infrastructure are approved.

### AI-ENRICHMENT-A — Gemini/Groq provider foundation

**Status:** Configuration foundation committed; provider implementation not started.

1. Define one provider-neutral request/result contract and strict Pydantic output schemas.
2. Implement Gemini and Groq SDK clients behind the same interface.
3. Select one primary provider; use the configured secondary only for eligible retryable failures. Do not duplicate every request.
4. Apply content-hash plus prompt/schema-version caching to avoid repeat calls.
5. Bound input characters, output tokens, timeouts and retries; classify quota, timeout, malformed and provider errors.
6. Validate all model output. Preserve original descriptions and send unresolved/low-confidence output to exception handling.
7. Add mocked unit tests for both providers, failover, cache hits, malformed output, quota exhaustion, timeouts and disabled mode.
8. Never log API keys or unnecessary personal data. AI remains disabled until local credentials and explicit smoke testing.

**Acceptance:** deterministic extraction works with AI disabled; both providers satisfy the same contract under mocked tests; fallback and caching are bounded; AI cannot affect hard gates or publish.

### M4-SA-B — Workable adapter implementation

**Status:** Adapter code and mocked tests added; live employer validation and frontend/API integration verification pending. On 12 November 2026, Workable URL detection, discovery/inspection routes, shared source preview registration and employer onboarding support were committed to `dev`. The user reported 12 focused adapter tests passing before these integration changes; new route/parser tests, frontend typecheck/build and repository quality gates are awaiting CI/local verification.

1. Implemented the documented public careers endpoint client behind the existing ATS adapter contract. The board slug remains employer/source configuration.
2. Test the South African cohort: LekkeSlaap, Electrum and GoTyme Bank.
3. Verify board identity, response schema, complete vacancy counts, stable IDs, full descriptions, locations, exact advert/application URLs, redirects, rate limits and bounded failure behavior.
4. Distinguish the documented public careers endpoint from Workable's authenticated customer SPI API. Do not require employer credentials or imply the public widget is a vendor-supported API.
5. Mocked tests cover public endpoint routing, redirects, invalid slugs, rate limits, normalization, malformed records and duplicate IDs. Expand fixture coverage for transient failures and live partial-board behavior. Partial retrieval must not expire missing vacancies.

**Verification so far:** GitHub Actions ran the backend suite: 216 passed, 1 skipped. The run was marked failed by the repository-wide line-limit test because four unrelated existing files exceed 100 lines (`backend/scout/branding/logo_discovery.py`, `backend/scout/api/employers.py`, `frontend/src/employer-onboarding/useEmployerRegistration.ts`, `frontend/src/employer-onboarding/EmployerOnboardingPanel.tsx`). The dedicated line-limit and naming scripts were skipped after the test failure. The repository formatting workflow succeeded.

**Acceptance:** code and mocked tests are present. Checkpoint remains open until live retrieval is validated against representative boards, vacancy counts/completeness and application destinations are reviewed, and repository quality checks pass. HTTP 200 alone is not acceptance.

### M4-SA-C — Workday adapter implementation

**Status:** Reactivated; follows Workable; not started.

1. Start with the Old Mutual board mapping in the employer/source registry. Verify the current official careers URL and its Workday relationship.
2. Parse host cluster, tenant, site and locale independently from the official board URL; do not hardcode employer values in adapter code.
3. Implement bounded CXS listing POST requests, pagination and per-vacancy detail retrieval using the observed `externalPath` behavior.
4. Verify result totals/caps, stable IDs, description completeness, locations, redirects and exact application URLs. Pick n Pay remains an unverified lead until its official site mapping is established.
5. Add fixtures and tests for multiple tenants, page boundaries, caps, empty, malformed, blocked, rate-limited and partial outcomes.

**Acceptance:** one configuration-driven Workday adapter works against at least two independently verified employer boards without employer-specific code changes. The observed CXS route remains labelled undocumented and is revalidated before production use.

### M4-SA-D — SAP SuccessFactors employer-specific investigation

**Status:** Planned after Workable and Workday; no adapter implementation is assumed.

1. Reconfirm the current official careers entry points and SuccessFactors relationship for Sanlam and Capitec Bank. Treat historical mappings as leads, not current proof.
2. Use Crawlee HTTP-first to inspect redirects, page HTML, canonical links, sitemaps, `JobPosting` structured data, embedded JSON/configuration and publicly accessible network requests.
3. Record each employer's observed site type, request method, endpoint pattern, tenant/site identifiers, pagination, vacancy totals, detail route, stable IDs and application destination behavior in its source configuration and evidence.
4. Use bounded Playwright only if the public page requires browser execution and access is permitted. Do not bypass authentication, CAPTCHA, robots/terms restrictions or anti-bot controls.
5. Do not build on the retiring legacy SuccessFactors RSS/XML response.
6. Compare the two employer implementations. Build one reusable SuccessFactors adapter only if they share a stable, permitted retrieval contract. If not, retain the generic Crawlee path with explicit per-employer retrieval profiles; do not create bespoke adapter code per employer.

**Acceptance:** current employer/platform relationships and public retrieval behavior are evidenced separately. A reusable adapter is approved only if common behavior is demonstrated; otherwise the employer-specific generic crawler route is documented with its limits and test fixtures.

### M4-SA-G — Additional platform investigation

Continue with SmartRecruiters, BambooHR, Breezy HR, Simplify.hr, eRecruit and other candidates according to verified South African employer coverage. Keep eRecruit distinct from Graylink Neptune. Implement only when a reliable, permitted public retrieval method is demonstrated.

## Local configuration

The backend uses optional extras:

- `dev`: pytest and Ruff.
- `crawler`: Crawlee with Playwright integration.
- `ai`: Google GenAI and Groq SDKs.

Install from `backend/`:

```bash
python -m pip install -e ".[dev,crawler,ai]"
```

Copy any missing variables from `.env.example` into the ignored local `.env`. Configure API keys locally only. Model identifiers must be selected and verified against current provider availability and account quotas. Keep `AI_ENABLED=false` and `CRAWLER_ENABLED=false` until local tests are complete.

## Quality and review gates

- Every handwritten source/test file remains at or below 100 physical lines.
- Run `python3 scripts/check-file-line-limits.py` and `python3 scripts/check-naming-conventions.py`.
- Unit tests use fixtures/mocks; live site tests are separately identified.
- Record exact commands, results, source evidence, limitations and commits.
- Do not claim adapter support without representative live validation.
- Do not mark a checkpoint Accepted without explicit user review.
- No Apify hosting, paid AI plan, Zyte paid upgrade/API usage, production deployment or new database is approved. Zyte Scrapy Cloud's included student unit is approved for a manually verified worker deployment; recurring scheduling remains gated by M4-SA-E acceptance.
