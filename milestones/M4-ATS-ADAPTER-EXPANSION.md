# M4 — First-Wave ATS Adapter Expansion

**Status:** Teamtailor M4-TEAMTAILOR-A/B implemented and CI-verified; awaiting user review. Ashby remains deferred; Lever M4-LEVER-A and M4-LEVER-B accepted.  
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
|     2 | Lever      | **Accepted — 9 November 2026**                 | **Accepted — 10 November 2026**  | Mama Money, Theodo, Wing Assistant. Verify public Postings API, regional host behavior, pagination and exact posting/apply URLs.                                                        |
|     3 | Teamtailor | **Implemented — 10 Nov 2026**                  | **Implemented — 10 Nov 2026**    | Root Platform, Footasylum, TeamViewer. Verify public RSS feed, custom-domain handling, feed completeness and destination URLs.                                                          |
|     4 | Personio   | **M4-PERSONIO-A**                              | **M4-PERSONIO-B**                | ottonova, Open, Openprovider. Verify XML feed availability, employer enablement requirements, fields and detail/application destinations.                                               |
|     5 | Recruitee  | **M4-RECRUITEE-A**                             | **M4-RECRUITEE-B**               | TransPerfect, Fastned, Tether. Verify current public XML offer feed availability, completeness, stable IDs and exact destinations; do not rely on the token-protected Careers Site API. |
|     6 | Workable   | **M4-WORKABLE-A**                              | **M4-WORKABLE-B**                | LekkeSlaap, Electrum, GoTyme Bank. Verify observed public careers-widget JSON behavior, board completeness, detail handling and application URLs.                                       |

## First checkpoint instruction

Ashby remains deferred following the user's explicit instruction; await its partner response before reopening it. Lever M4-LEVER-A and M4-LEVER-B are accepted. Teamtailor M4-TEAMTAILOR-A/B implementation and CI verification are complete on branch `dev`. Stop for user review; do not start Personio until Teamtailor is accepted.

The next planned adapter is Personio. Do not begin it until the user has reviewed and accepted the Teamtailor A/B checkpoint pair.

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

## M4-LEVER-A acceptance and M4-LEVER-B progress — 9 November 2026

The user directed progression to M4-LEVER-B after reviewing the Lever implementation and local verification results. Record M4-LEVER-A as accepted.

A verification evidence supplied by the user:

- `pytest test-suites/unit-tests/ats-adapters/lever-adapter -q`: **10 passed in 0.91s**.
- `python3 scripts/check-file-line-limits.py`: passed; all scanned source files satisfy the 100-line limit.
- `python3 scripts/check-naming-conventions.py`: failed with 38 repository-wide violations. None of the listed paths is a new Lever adapter source/test file. The findings include unrelated backend/frontend paths and generated pytest/Ruff cache directories; do not claim the repository-wide naming gate passed.

M4-LEVER-B implementation now committed on `dev`:

- Registers `LeverSourceAdapter` in the shared `SourceExtractionService`; Greenhouse remains unchanged.
- Marks Lever implemented in the generic ATS registry and restricts the region setting to `global` or `eu`.
- Adds pending, non-activated employer/source configuration for Mama Money, Theodo and Wing Assistant. Employer identity/source relationship and permission remain pending administrator verification.
- Adds Lever to source create/update API contracts and adds HTTPS board URL parsing plus Lever inspection/discovery routes.
- Extends the admin onboarding/source-management flow to detect Lever board URLs and persist the returned slug/region configuration. Discovery parses and validates the URL only; vacancy retrieval remains in the explicit inspection or extraction step.
- Adds tests for registry configuration, shared adapter registration, source API creation, URL parsing and URL-only discovery.

**B verification still required:** run the focused Lever tests, full backend unit suite, backend formatting/lint checks, frontend typecheck/build/lint, mandatory line-limit and naming checks, and representative live validation through the new API/admin flow. No local execution of these B checks is claimed yet. Confirm that the extraction endpoint persists Lever vacancies through the existing repositories, preserves incomplete-run semantics, and remains idempotent across repeated runs.

## M4-LEVER-B acceptance — 10 November 2026

The user reviewed the end-to-end admin results and accepted the Lever integration. Lever is closed for this milestone; proceed to Teamtailor M4-TEAMTAILOR-A.

**Integration and live evidence confirmed by the user:**

- Lever source discovery and employer onboarding work through the frontend, including automatic employer-name fallback for Lever boards.
- Vacancy extraction completed and persisted jobs for companies registered directly through the admin UI and for a company configured through the backend/registry path.
- The Companies directory displays the registered employers and their extracted vacancy counts. The Jobs workspace displays the extracted vacancy records.
- The user confirmed the Lever workflow is working and approved closing the checkpoint.

**Regression evidence supplied by the user:**

- Backend: `pytest test-suites/unit-tests -q` — **160 passed**.
- Frontend: `npm run typecheck` — passed.
- Frontend: `npm run build` — passed.
- Frontend: `npm run lint:size` — passed; all scanned source files satisfy the 100-physical-line limit.
- Frontend: `npm run lint:naming` — passed; scanned files and directories satisfy naming standards.

The earlier generic `npm run lint` command is not a defined frontend script; the two explicit repository checks above are the available size and naming checks. Backend unit tests and frontend checks were run after the geography line-limit correction.

**Acceptance:** M4-LEVER-A and M4-LEVER-B are accepted. The Lever adapter is registered in the shared extraction service, available through admin onboarding, and verified with persisted live vacancy results. This acceptance does not claim that the full six-adapter M4 milestone is complete. Ashby remains deferred pending the partner response.

## M4-TEAMTAILOR-A investigation and implementation — 10 November 2026

The user supplied direct terminal evidence for the three registered test feeds:

- Root Platform: `https://root.teamtailor.com/jobs.rss`, 3 vacancies.
- Footasylum: `https://footasylum.teamtailor.com/jobs.rss`, 80 vacancies.
- TeamViewer: `https://careers.teamviewer.com/jobs.rss`, 100 vacancies in the default response.
- TeamViewer pagination: `?per_page=2` returned two items; `?offset=100&per_page=2` returned different later items.
- The feeds use RSS 2.0 and the Teamtailor location namespace. Observed fields and limitations are recorded in `docs/ATS-PLATFORM-RESEARCH.md`.

Implementation uses the existing `ATSAdapter` contract and shared extraction/preview services. It does not introduce a separate extraction pipeline. Provider-specific modules own careers-URL validation, RSS parsing, bounded pagination, failure classification and vacancy mapping. The frontend probes the Teamtailor feed before falling back to Greenhouse for non-Lever careers URLs; this allows custom Teamtailor domains without hardcoding employer hostnames.

Implementation files:

- `backend/scout/ats_adapters/teamtailor_adapter/`
- `backend/scout/api/teamtailor_routes.py`
- `backend/test-suites/unit-tests/ats-adapters/teamtailor-adapter/`

Integration changes add Teamtailor to both shared adapter factories, backend create/update contracts, frontend adapter contracts, API router registration, onboarding discovery and preview URL selection. The generic adapter registry now records public RSS pagination support and the correct `{careers_url}.rss` endpoint pattern. Employer/source registry entries are technical test configurations only; notes explicitly leave administrator verification and activation pending.

**Important mapping boundary:** Teamtailor's `link` is the vacancy advert page. The adapter preserves it exactly and uses it as the available user-facing destination; it does not claim the feed supplies a direct application-form URL. `source_updated_at` remains null because no such timestamp was observed. Remote status, role, division, optional company metadata and location details remain in the raw provider payload where the shared vacancy contract has no dedicated fields.

**Verification status:** focused deterministic tests cover URL parsing, Teamtailor namespace and field mapping, offset pagination, incomplete later-page behavior, empty and malformed feeds, multiple locations, description sanitization, required identity fields, HTTP failures, timeouts, route discovery/fallback and shared registry/service registration. GitHub Actions architecture compliance is green. The user manually verified the public feeds; a live extraction through the new adapter and administrator approval/activation of employer sources remain outstanding.

### Teamtailor CI remediation — 10 November 2026

The first GitHub Actions architecture-compliance run after the Teamtailor implementation executed the complete backend suite: **176 passed, 1 skipped, 1 failed**. The only failure was the repository-wide line-limit test, which identified two pre-existing files that the formatter had expanded to 101 lines: `backend/scout/geography.py` and `frontend/src/job-management/VacancyRecordCard.tsx`. The formatting workflow also expanded the Teamtailor pagination client beyond the 100-line standard. These responsibilities were split into focused modules. The next compliance run passed backend tests, the repository-wide line-limit check and naming-convention check. No Teamtailor test failure was reported in that run.

The second architecture-compliance run identified a missing Teamtailor entry in the company directory's ATS label map. That entry was added. The subsequent complete compliance run passed all backend, repository-quality and frontend gates.

### Final Teamtailor verification — 10 November 2026

GitHub Actions run `42797905496` completed successfully for implementation commit `ca6d791878599aa79032a0f9e0b1864fb6974876`:

- Backend unit and integration suites: **187 passed, 1 skipped**.
- Repository-wide source line limit: passed.
- Descriptive naming conventions: passed.
- Frontend TypeScript typecheck: passed.
- Frontend production build: passed.

The repository formatting workflow completed successfully. The final documentation commit was checked by GitHub Actions run `42798126678`, which passed the backend suite, repository-quality checks, TypeScript typecheck and frontend production build. No Teamtailor code test currently depends on a live external feed. The three public RSS feeds were fetched manually by the user, and adapter behavior is covered by deterministic fixtures and mocked HTTP. A live end-to-end extraction from the running Scout API remains a post-pull validation step.

**Checkpoint state:** M4-TEAMTAILOR-A and M4-TEAMTAILOR-B are implemented and automated checks are green, but remain **awaiting user review/acceptance**. The three employer source configurations remain pending administrator verification and activation. Do not start Personio until the user accepts this checkpoint pair.

### Companies directory verification fix — 10 November 2026

The user's local Companies screenshot showed that Teamtailor was missing from the ATS filter. The card renderer already had a Teamtailor label, but the toolbar filter options did not. Added the Teamtailor filter option.

A second blocker was found while tracing why the registered Teamtailor test targets would not appear in the local directory after a registry import: the registry importer allowlist still excluded Teamtailor, and the database source-adapter CHECK constraint only allowed Greenhouse, Lever and Workday. Added Teamtailor to the importer allowlist and created migration `0011-add-teamtailor-adapter.sql`. The importer test now verifies a Teamtailor employer/source is imported.

**Local verification steps after pulling:**

1. Run `python -m scout.persistence.migration_runner` from `backend/` to apply migration 0011.
2. Run `python -m scout.registry_importer` from `backend/` to import the three Teamtailor test targets as discovered records.
3. Refresh Companies and select Teamtailor in the job-board filter. Root Platform, Footasylum and TeamViewer should then be listed, provided their records are not already present under conflicting normalized source URLs.

The registry importer is repeat-safe. It does not approve employers or verify source permission; those states remain subject to the existing review workflow.
