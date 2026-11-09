# M4 — First-Wave ATS Adapter Expansion

**Status:** In progress — Ashby deferred pending partner response; Lever M4-LEVER-A implementation committed, local verification pending  
**Scope:** Six first-wave ATS adapters only: Ashby, Lever, Teamtailor, Personio, Recruitee and Workable.  
**Checkpoint model:** Twelve checkpoints total — one A and one B for each adapter.

## Objective

Expand Scout beyond the existing Greenhouse adapter by implementing the six approved first-wave providers. Reuse the shared adapter contract and extraction pipeline. Greenhouse remains the architectural reference; it is not part of M4 delivery.

Second- and third-wave platforms, Placement Partner and Workday are outside this milestone. They must not be added to the M4 checkpoint register. Workday remains deferred.

## Required reading

Before starting an M4 checkpoint, read:

- `AGENTS.md`
- `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`
- `IMPLEMENTATION-PLAN.md`
- `TECHNICAL-APPROACH.md`
- `AI-WORKING-GUIDE.md`
- `CODING-STANDARDS.md`
- `docs/ATS-PLATFORM-RESEARCH.md`
- `docs/ATS-EMPLOYER-TEST-TARGETS.json`
- `backend/registry/ats-adapter-registry.json`
- `backend/registry/employer-source-registry.json`, if present

## Rules applying to all twelve checkpoints

- Every handwritten source-code file, including tests, must contain **100 physical lines or fewer**. Run `python3 scripts/check-file-line-limits.py` and `python3 scripts/check-naming-conventions.py`; do not minify code to pass.
- Keep each module focused on one responsibility. Separate URL/config validation, provider HTTP retrieval, response mapping, extraction orchestration, persistence, API routing and tests where the existing architecture requires them.
- Provider-specific HTTP, parsing, pagination and detail retrieval belong inside the adapter. Shared quality gates, deduplication, lifecycle and publishing remain in the shared pipeline.
- Employer-specific slugs, tenant identifiers and source URLs belong in the employer/source registry, not adapter code. Generic adapter capabilities and required configuration belong in the ATS adapter registry.
- Do not rewrite Greenhouse or create a separate ingestion pipeline for each ATS. Reuse proven boundaries where appropriate; adapt provider-specific behavior where evidence requires it.
- Distinguish successful empty boards from partial, blocked, malformed, rate-limited, timeout and transient failures. Failed or partial runs must never imply that vacancies disappeared.
- HTTP 200 alone is not acceptance. Verify stable vacancy identity, meaningful content, descriptions, locations, timestamps, completeness and exact vacancy/application destinations.
- Use deterministic fixtures/mocked HTTP for unit tests and contract tests. Record representative live evidence against the employer cohort.
- No Docker, paid infrastructure, deployment or hosting work in M4.
- Complete and review each adapter's A/B pair before starting the next adapter. If checkpoint A is evidence-backed blocked/deferred and the user explicitly approves deferral, record checkpoint B as deferred and proceed to the next adapter. Stop for user review at each completed checkpoint.

## Checkpoint responsibilities

### A — Investigate, design and implement

This is one checkpoint with two sequential activities:

1. **Investigation and design (no code commit):**
   - Inspect the real employer career pages and public provider retrieval behavior.
   - Verify source identification, request method/parameters, response shape, pagination/detail behavior, fields, board completeness, empty/error behavior and exact vacancy/application URLs.
   - Compare the target employers. Record confirmed evidence separately from assumptions, historical mappings and unresolved behavior.
   - Inspect the corresponding Greenhouse adapter modules, shared contracts, extraction service, API route, registries and tests.
   - Produce the evidence report and file-by-file implementation design. Identify reusable shared boundaries and provider-specific behavior.
2. **Implementation (code changes and commit):**
   - Implement the adapter according to the evidence and reviewed design.
   - Add focused unit tests and deterministic fixtures for provider parsing/mapping and relevant failure cases.
   - Keep employer-specific configuration out of adapter code.
   - Run the relevant focused tests and mandatory line-limit/naming checks before completing A.

**A deliverables:** evidence report; implementation design; adapter modules; focused unit tests/fixtures; recorded commands and results; implementation commit. The investigation activity itself must not commit code. If evidence does not establish a permitted, reliable retrieval method, stop and report the adapter as blocked/deferred instead of fabricating an implementation.

### B — Integrate and verify

- Register the generic adapter definition and employer/source-specific configurations in the correct registries.
- Connect the adapter to the existing shared extraction, persistence and quality/lifecycle workflow.
- Integrate URL detection/source configuration and the existing API/admin onboarding path where required by the current architecture. Do not duplicate shared workflows.
- Add or complete contract and integration tests covering the shared adapter contract, registry/configuration, persistence handoff and failure behavior.
- Verify idempotent employer/source handling and stable vacancy identity; ensure partial/failed extraction cannot expire or remove vacancies.
- Run relevant unit, contract, integration and regression tests, plus mandatory line-limit/naming checks.
- Perform representative live validation against the target employer cohort where reachable. Record exact requests/endpoints, observed counts, completeness, descriptions, destinations, failures and gaps.
- Record the commit(s), exact commands/results and evidence. Stop for user review before moving to the next adapter.

**B deliverables:** registry/configuration integration; shared-pipeline/API/admin integration as applicable; contract/integration/regression test results; live validation report; evidence-backed status and unresolved gaps.

## Adapter checkpoint register

Each adapter has exactly two checkpoints. Complete A before B, and complete/review B before beginning the next adapter.

| Order | Adapter    | Checkpoint A — investigate, design, implement  | Checkpoint B — integrate, verify | Employer test cohort and investigation focus                                                                                                                                            |
| ----: | ---------- | ---------------------------------------------- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|     1 | Ashby      | **Deferred — enquiry sent; awaiting response** | **Deferred**                     | Midnite, MyEdSpace, Tree Traction. Reopen only after Ashby confirms partner-feed eligibility, feed access and employer opt-in requirements; see the Ashby investigation report.         |
|     2 | Lever      | **In progress — implementation committed; local verification pending** | **M4-LEVER-B**                   | Mama Money, Theodo, Wing Assistant. Verify public Postings API, regional host behavior, pagination and exact posting/apply URLs.                                                        |
|     3 | Teamtailor | **M4-TEAMTAILOR-A**                            | **M4-TEAMTAILOR-B**              | Root Platform, Footasylum, TeamViewer. Verify public RSS feed, custom-domain handling, feed completeness and destination URLs.                                                          |
|     4 | Personio   | **M4-PERSONIO-A**                              | **M4-PERSONIO-B**                | ottonova, Open, Openprovider. Verify XML feed availability, employer enablement requirements, fields and detail/application destinations.                                               |
|     5 | Recruitee  | **M4-RECRUITEE-A**                             | **M4-RECRUITEE-B**               | TransPerfect, Fastned, Tether. Verify current public XML offer feed availability, completeness, stable IDs and exact destinations; do not rely on the token-protected Careers Site API. |
|     6 | Workable   | **M4-WORKABLE-A**                              | **M4-WORKABLE-B**                | LekkeSlaap, Electrum, GoTyme Bank. Verify observed public careers-widget JSON behavior, board completeness, detail handling and application URLs.                                       |

## First checkpoint instruction

Ashby is deferred following the user's explicit instruction. The user confirmed an enquiry email was sent on 9 November 2026; await Ashby's response before reopening Ashby. Proceed with **M4-LEVER-A** on branch `dev`.

Read the required repository guidance and inspect the Greenhouse reference implementation before investigating Lever. Use Mama Money, Theodo and Wing Assistant as the employer cohort. Inspect their actual careers pages and public network/API behavior. Verify the public request, parameters, regional host, response structure, pagination, detail retrieval, stable IDs, descriptions, locations, timestamps, empty/error behavior and exact vacancy/application URLs. Compare behavior across the three employers.

Lever's official Postings API documentation states that published postings are publicly viewable and may be scraped by third parties. Use only this public published-postings API; do not use authenticated Lever API endpoints or internal/unlisted postings. Produce the evidence report and file-by-file design first. **Do not commit code during investigation.** Implement the Lever adapter and focused unit tests only after the three-employer evidence establishes reliable, complete retrieval. Keep every handwritten source/test file within 100 physical lines. Record the implementation commit and exact test/check results. Stop for review before M4-LEVER-B.

## M4 acceptance

- All six first-wave adapters have completed their A and B checkpoints, or have an evidence-backed blocked/deferred outcome.
- Each implemented adapter has verified source behavior, configuration, URL detection, stable IDs, vacancy fields and exact candidate destinations.
- Each adapter is integrated with the shared extraction/persistence/quality/lifecycle workflow and passes relevant unit, contract, integration and regression tests.
- Representative live validation is recorded for the target employer cohort; inaccessible or unsupported targets are explicitly identified.
- Adding another employer to a supported platform requires configuration, not employer-specific adapter code.
- Failed or partial extraction cannot imply that vacancies disappeared or expired.
- All handwritten source-code files and tests remain within the 100-line limit.
- The user reviews each checkpoint before work proceeds to the next checkpoint.


## Lever M4-LEVER-A implementation update — 9 November 2026

Live local requests verified 513 postings across Mama Money (7), Theodo (131) and Wing Assistant (375), with 513 unique IDs, no missing IDs, 11 Cape Town matches, and exact job/application URLs. Pagination completed with short final pages on all three boards.

Wing Assistant has 56 records without `descriptionPlain`; the Cape Town Inside Sales Manager record was verified to contain a 1,362-character HTML description in both list and detail responses. The adapter prefers plain text and falls back to standard-library HTML-to-text extraction. If both are absent, description remains null for shared completeness gates. The raw provider payload is retained.

Implementation files:
- `backend/scout/ats_adapters/lever_adapter/lever_source_adapter.py`
- `backend/scout/ats_adapters/lever_adapter/lever_postings_client.py`
- `backend/scout/ats_adapters/lever_adapter/lever_pagination.py`
- `backend/scout/ats_adapters/lever_adapter/lever_postings_contracts.py`
- `backend/scout/ats_adapters/lever_adapter/lever_response_mapper.py`
- `backend/scout/ats_adapters/lever_adapter/lever_description_parser.py`
- `backend/scout/ats_adapters/lever_adapter/lever_vacancy_mapper.py`
- Focused unit tests in `backend/test-suites/unit-tests/ats-adapters/lever-adapter/`

The adapter uses explicit `slug` and `region` configuration; current targets use the global host. It leaves `published_at` and `source_updated_at` null because the observed `createdAt` field is undocumented and its semantics are not established. Registry activation and registration in the shared extraction service are reserved for checkpoint B.

**Verification status:** Tests and mandatory repository checks have not yet been run in the user's local checkout. M4-LEVER-A remains in progress until those checks are run and the user reviews the implementation. Do not begin M4-LEVER-B before that review.
