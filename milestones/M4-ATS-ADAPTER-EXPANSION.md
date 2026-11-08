# M4 — First-Wave ATS Adapter Expansion

**Status:** Not started  
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
- Complete and review each adapter's A/B pair before starting the next adapter. Stop for user review at each checkpoint.

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

| Order | Adapter | Checkpoint A — investigate, design, implement | Checkpoint B — integrate, verify | Employer test cohort and investigation focus |
|---:|---|---|---|---|
| 1 | Ashby | **M4-ASHBY-A** | **M4-ASHBY-B** | Midnite, MyEdSpace, Tree Traction. Verify public Job Postings API, board identity, response completeness, descriptions and application URLs. |
| 2 | Lever | **M4-LEVER-A** | **M4-LEVER-B** | Mama Money, Theodo, Wing Assistant. Verify public Postings API, regional host behavior, pagination and exact posting/apply URLs. |
| 3 | Teamtailor | **M4-TEAMTAILOR-A** | **M4-TEAMTAILOR-B** | Root Platform, Footasylum, TeamViewer. Verify public RSS feed, custom-domain handling, feed completeness and destination URLs. |
| 4 | Personio | **M4-PERSONIO-A** | **M4-PERSONIO-B** | ottonova, Open, Openprovider. Verify XML feed availability, employer enablement requirements, fields and detail/application destinations. |
| 5 | Recruitee | **M4-RECRUITEE-A** | **M4-RECRUITEE-B** | TransPerfect, Fastned, Tether. Verify current public XML offer feed availability, completeness, stable IDs and exact destinations; do not rely on the token-protected Careers Site API. |
| 6 | Workable | **M4-WORKABLE-A** | **M4-WORKABLE-B** | LekkeSlaap, Electrum, GoTyme Bank. Verify observed public careers-widget JSON behavior, board completeness, detail handling and application URLs. |

## First checkpoint instruction

Start with **M4-ASHBY-A** on branch `dev`.

Read the required repository guidance and inspect the Greenhouse reference implementation before investigating Ashby. Use Midnite, MyEdSpace and Tree Traction as the employer cohort. Inspect their actual careers pages and public network/API behavior. Verify the public request, parameters, response structure, completeness, pagination/detail needs, stable IDs, descriptions, locations, timestamps, empty/error behavior and exact vacancy/application URLs. Compare behavior across the three employers.

Map the findings to the existing adapter contract and shared extraction/persistence workflow. Produce the evidence report and file-by-file design first. **Do not commit code during investigation.** Once the investigation establishes a reliable and permitted retrieval method and the design is ready, implement the Ashby adapter and focused unit tests as the implementation activity within M4-ASHBY-A. Keep every handwritten source/test file within 100 physical lines. Record the implementation commit and exact test/check results. Stop for review before M4-ASHBY-B.

## M4 acceptance

- All six first-wave adapters have completed their A and B checkpoints, or have an evidence-backed blocked/deferred outcome.
- Each implemented adapter has verified source behavior, configuration, URL detection, stable IDs, vacancy fields and exact candidate destinations.
- Each adapter is integrated with the shared extraction/persistence/quality/lifecycle workflow and passes relevant unit, contract, integration and regression tests.
- Representative live validation is recorded for the target employer cohort; inaccessible or unsupported targets are explicitly identified.
- Adding another employer to a supported platform requires configuration, not employer-specific adapter code.
- Failed or partial extraction cannot imply that vacancies disappeared or expired.
- All handwritten source-code files and tests remain within the 100-line limit.
- The user reviews each checkpoint before work proceeds to the next checkpoint.
