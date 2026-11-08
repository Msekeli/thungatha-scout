# M4 — ATS Adapter Expansion

**Status:** Not started  
**Delivery rule:** Every ATS adapter gets two checkpoints: (1) investigate and design; (2) implement, integrate and verify. Do not turn M4 into one large task, and do not create a separate checkpoint for every small coding activity.

## Objective

Expand Scout's employer-source coverage beyond Greenhouse while retaining one shared ingestion pipeline. Implement the platforms in the approved waves. Greenhouse is the existing architectural reference, not another adapter to build.

## Required reading

Before starting any M4 checkpoint, read:

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

## Rules applying to every adapter

- Every handwritten source-code file, including tests, must contain **100 physical lines or fewer**. Run `python3 scripts/check-file-line-limits.py`; do not minify code to pass.
- Keep single responsibilities separate. URL recognition/config validation, provider HTTP retrieval, response mapping, extraction orchestration, persistence, API routing and tests must not be bundled into one oversized or multi-purpose module.
- Provider-specific HTTP, pagination, parsing and detail retrieval belong inside the adapter. Shared quality gates, deduplication, lifecycle and publishing remain in the shared pipeline.
- Keep employer-specific slugs, tenant identifiers and source URLs in the employer/source registry, not hardcoded in adapter code. Generic adapter capabilities and required configuration belong in the ATS adapter registry.
- Use deterministic fixtures/mocked HTTP for unit tests. Add contract coverage and live smoke evidence for real employer boards.
- Distinguish successful empty boards from partial, blocked, malformed, rate-limited, timeout and transient failures. Failed or partial runs must never imply that vacancies disappeared.
- HTTP 200 alone is not acceptance. Verify stable vacancy identity, meaningful content, descriptions, locations, timestamps, completeness and exact vacancy/application destinations.
- Do not rewrite Greenhouse or create a separate ingestion pipeline per ATS. Reuse its proven boundaries where appropriate; adapt provider-specific behavior where it differs.
- Workday remains deferred. Do not start a later wave before the preceding wave's review gate. No Docker, paid infrastructure, deployment or hosting work in M4.

## Two-checkpoint pattern

**Checkpoint A — Investigate and design**

- Inspect the actual employer career pages and the provider's public retrieval behavior.
- Verify URL/tenant/slug identification, request method and parameters, response structure, pagination/detail behavior, available fields, completeness, error/empty behavior and candidate destination URLs.
- Use the employer test cohort recorded in the JSON registry. Test multiple employers where the cohort provides them; distinguish confirmed evidence from directory leads and historical mappings.
- Inspect the corresponding Greenhouse modules and tests. Map the new provider's behavior onto the existing adapter contract and shared pipeline.
- Produce a concise evidence report and a file-by-file implementation design. Identify what can be reused, what differs and what remains uncertain.
- **No application-code changes in this checkpoint.** Stop for review if the retrieval method or source behavior is not sufficiently established.

**Checkpoint B — Implement, integrate and verify**

- Implement the smallest adapter consistent with the reviewed design.
- Keep each module within the 100-line limit and each module focused on one responsibility.
- Register the generic adapter definition and the employer/source-specific configuration in their correct registries.
- Connect to the existing shared extraction/persistence workflow and existing API/admin onboarding path; do not duplicate those workflows.
- Add unit/contract tests for valid and invalid URLs/config, normal and empty results, malformed responses, partial results and provider failures as applicable.
- Run repository quality gates and relevant regression tests. Perform representative live validation against the employer cohort where the source is reachable.
- Record actual commands/results, live evidence, gaps and the next adapter. User reviews the checkpoint before the next adapter begins.

## Adapter checkpoint register

Each row below is one adapter with exactly two checkpoints. Checkpoint A is investigation/design; Checkpoint B is implementation/integration/verification.

| Order | Adapter / source   | Checkpoint A          | Checkpoint B          | Target cohort / special condition                                                                   |
| ----- | ------------------ | --------------------- | --------------------- | --------------------------------------------------------------------------------------------------- |
| 1     | Ashby              | M4-ASHBY-A            | M4-ASHBY-B            | Midnite, MyEdSpace, Tree Traction                                                                   |
| 2     | Lever              | M4-LEVER-A            | M4-LEVER-B            | Mama Money, Theodo, Wing Assistant; verify regional host and pagination                             |
| 3     | Teamtailor         | M4-TEAMTAILOR-A       | M4-TEAMTAILOR-B       | Root Platform, Footasylum, TeamViewer; RSS and custom-domain handling                               |
| 4     | Personio           | M4-PERSONIO-A         | M4-PERSONIO-B         | ottonova, Open, Openprovider; XML feed may need employer enablement                                 |
| 5     | Recruitee          | M4-RECRUITEE-A        | M4-RECRUITEE-B        | TransPerfect, Fastned, Tether; prefer public XML feed, verify current availability                  |
| 6     | Workable           | M4-WORKABLE-A         | M4-WORKABLE-B         | LekkeSlaap, Electrum, GoTyme Bank; validate observed public widget behavior                         |
| 7     | SmartRecruiters    | M4-SMARTRECRUITERS-A  | M4-SMARTRECRUITERS-B  | WNS Global Services, OUTsurance, Anglo American; verify each live board                             |
| 8     | BambooHR           | M4-BAMBOOHR-A         | M4-BAMBOOHR-B         | Integrity360, Platform45, TreasuryONE; list/detail behavior                                         |
| 9     | Breezy HR          | M4-BREEZY-A           | M4-BREEZY-B           | ShopriteX, Lula, Absolute Pets, Totalstay, City Lodge Hotels; prove description/detail completeness |
| 10    | Simplify.hr        | M4-SIMPLIFY-A         | M4-SIMPLIFY-B         | Media24, homechoice, Adendorff, Dis-Chem; discover actual public retrieval behavior                 |
| 11    | Zoho Recruit       | M4-ZOHO-A             | M4-ZOHO-B             | Chancen is the only confirmed employer target; do not invent more                                   |
| 12    | SAP SuccessFactors | M4-SUCCESSFACTORS-A   | M4-SUCCESSFACTORS-B   | Sanlam, Gold Fields and Sasol are historical/variable leads; re-verify current tenant behavior      |
| 13    | eRecruit / Neptune | M4-ERECRUIT-NEPTUNE-A | M4-ERECRUIT-NEPTUNE-B | Investigate eRecruit portals separately from Graylink Neptune; do not claim they are the same ATS   |

**Order within waves:** Rows 1–6 are first wave; 7–9 second wave; 10–13 third wave. Complete and review each adapter's A/B pair before moving to the next adapter. Complete a wave review before beginning the next wave. If investigation proves a source is inaccessible, unsupported or partner-dependent, record the evidence and mark implementation blocked/deferred rather than fabricating an adapter.

## Separate pipeline: Placement Partner

Placement Partner is a recruitment/staffing source, not a direct-employer ATS. Keep it separate from the ATS adapter rows:

- **M4-PLACEMENT-PARTNER-A:** investigate agency IDs, public listing/detail retrieval, redirects and exact candidate application destinations.
- **M4-PLACEMENT-PARTNER-B:** implement a separate agency-source workflow only after the investigation proves a permitted and reliable retrieval method.

JobAdder remains customer/partner-authorised unless a separate public route is proven. Leaply remains a discovery lead, not a confirmed public ATS adapter. Workday is deferred until explicitly reactivated.

## First next-chat instruction

Start with **M4-ASHBY-A — investigation and design only**.

> We are starting M4-ASHBY-A in Thungatha Scout, branch `dev`. Read all required repository guidance and the M4 document first. Investigate Ashby using Midnite, MyEdSpace and Tree Traction. Inspect their actual careers pages and public network/API behavior. Verify the exact public request, parameters, response structure, board completeness, pagination/detail needs, stable IDs, descriptions, locations, timestamps, empty/error behavior and exact vacancy/application URLs. Compare the observed behavior across employers.
>
> Treat Greenhouse as the architectural reference. Inspect `greenhouse_adapter.py`, `greenhouse_contracts.py`, `greenhouse_response_mapper.py`, `greenhouse_board_resolver.py`, `application/greenhouse_extraction_service.py`, the Greenhouse API route, registry entries and relevant tests. Map Ashby's behavior to the existing contracts and shared extraction/persistence flow. State which responsibilities can be reused and which require Ashby-specific handling. Do not copy Greenhouse blindly.
>
> This is investigation/design only: do not change application code, add dependencies or implement the adapter. Produce a concise evidence report and proposed file-by-file design for M4-ASHBY-B. Every proposed handwritten source file and test must be no more than 100 physical lines. Keep URL/config validation, HTTP retrieval, response mapping, extraction orchestration, persistence and API routing separated by single responsibility. Stop for review.

## M4 acceptance

- Each adapter has completed its investigation/design checkpoint and implementation/integration/verification checkpoint, or has an evidence-backed blocked/deferred outcome.
- Each implemented adapter passes relevant unit and contract tests and representative live validation.
- Employer/source relationships, retrieval method, required config, stable IDs, vacancy fields and exact candidate destinations are evidenced.
- All adapters use the shared extraction/persistence/quality/lifecycle pipeline.
- Adding another employer to a supported platform requires configuration, not employer-specific adapter code.
- Every handwritten source-code file and test is within the 100-line limit.
- The user reviews each adapter and each wave before work proceeds.
