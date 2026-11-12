# M4-SA — Crawlee Careers Discovery and Platform Coverage

**Status:** Planned; implementation not started  
**Updated:** 12 November 2026  
**Branch:** `dev`  
**Architecture decision:** Crawlee for Python; Gemini and Groq as optional AI providers

## Objective

Improve verified South African employer coverage through bounded discovery of official careers pages, evidence-based ATS fingerprinting and reusable generic extraction. Preserve the existing ATS adapter contract and shared Scout ingestion pipeline.

This milestone does not approve a new employer/source, bypass source restrictions, deploy a hosted crawler, or provision paid infrastructure.

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

**Status:** Not started.

1. Inspect the current repository, worker entry points, extraction service, adapter contracts, persistence and registries. Do not duplicate existing responsibilities.
2. Implement a small Crawlee execution boundary with bounded request/depth/domain scope, concurrency, response bytes, timeout, retry and graceful shutdown settings.
3. Capture requested/final/canonical URLs, status, content type, timestamps, relevant links, platform evidence, robots outcome, completeness and explicit failure classification.
4. Route known ATS fingerprints to existing adapters without generic duplicate retrieval.
5. Parse only public non-standard pages through a generic observation/extraction contract.
6. Persist observations through existing Scout repositories/services; do not retain full HTML by default.
7. Add deterministic fixtures and mocked tests for redirects, link scope, fingerprints, robots/blocked outcomes, malformed responses, timeouts, partial crawls and duplicate routing.
8. Verify partial/failed crawls cannot mark vacancies removed or expired.
9. Run focused tests and mandatory repository line-limit/naming checks.

**Acceptance:** local bounded crawler works; provenance and completeness are recorded; known ATS routing is tested; generic page observations enter the shared pipeline; failures are explicit and safe. Live employer smoke tests are recorded separately.

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

### M4-SA-B — Enterprise platform investigation

Investigate SAP SuccessFactors (Sanlam and Capitec leads), Workday and Oracle Recruiting Cloud. Verify official career URLs, redirects, public request/response behavior, completeness, stable IDs, descriptions and exact application URLs before designing an adapter.

### M4-SA-C — Local and mid-market platform investigation

Investigate Simplify.hr, eRecruit, BambooHR, Breezy HR and Workable. Keep eRecruit distinct from Graylink Neptune. Record employer/platform evidence and source constraints.

### M4-SA-D — Evidence-ranked integration

Implement only platforms with verified employer relevance and a reliable, permitted public retrieval method. Reuse the existing ATS contract, registries and shared pipeline. Do not implement based solely on vendor popularity or a successful HTTP 200.

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
- No Apify hosting, paid AI plan, scheduled cloud workload, production deployment or new database is approved.
