# M4 — ATS Adapter Expansion

**Status:** Not started  
**Milestone rule:** Deliver this milestone as small, independently reviewable checkpoints. Do not attempt all ATS platforms or the entire milestone in one implementation pass.

## Objective

Extend Scout's employer-source coverage beyond the implemented Greenhouse adapter while retaining one shared ingestion pipeline. The first new adapter is Ashby, followed by the remaining platforms in the approved waves.

## Authority and references

Read these before starting:
- `AGENTS.md`
- `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`
- `IMPLEMENTATION-PLAN.md`
- `TECHNICAL-APPROACH.md`
- `AI-WORKING-GUIDE.md`
- `CODING-STANDARDS.md`
- `docs/ATS-PLATFORM-RESEARCH.md`
- `docs/ATS-EMPLOYER-TEST-TARGETS.json`
- `backend/registry/ats-adapter-registry.json`
- `backend/registry/employer-source-registry.json` (if present; inspect actual tree)

Greenhouse is the working reference, not a template to copy blindly. Inspect its URL parsing, contracts, HTTP retrieval, response mapping, extraction orchestration, API inspection route, registry configuration and tests. Reuse the proven boundaries where they fit. Where Ashby differs, preserve the same responsibilities while adapting the provider-specific behavior. Do not create a second ingestion pipeline for each ATS.

## Non-negotiable implementation rules

1. **100-line limit:** every handwritten source-code file, including tests, must contain no more than 100 physical lines. Run `python3 scripts/check-file-line-limits.py`. Split larger modules by cohesive responsibility; do not minify or compress code.
2. **Single responsibility:** keep URL recognition/config parsing, provider HTTP transport, response mapping/normalization, extraction orchestration, persistence, API routing and tests in separate focused modules where the existing architecture requires them. Do not combine unrelated responsibilities to reduce file count.
3. **Adapter boundary:** provider-specific HTTP, pagination, parsing and detail retrieval belong inside the adapter. Shared quality gates, deduplication, lifecycle and publishing remain shared.
4. **Configuration:** board slugs, tenant identifiers and employer-specific source URLs belong in the employer/source registry, not hardcoded in adapter code. Generic capabilities and required config belong in the ATS adapter registry.
5. **Evidence:** a 200 response is not proof of complete extraction. Verify stable IDs, meaningful titles, descriptions, locations, timestamps, full-board completeness and exact vacancy/application URLs.
6. **Failure semantics:** distinguish successful empty boards from blocked, malformed, partial, rate-limited, timeout and transient failures. A partial/failed extraction must never be treated as evidence that vacancies disappeared.
7. **Tests:** unit tests use deterministic fixtures/mocked HTTP. Add contract tests for the common adapter behavior and explicit integration/smoke evidence for real employer boards.
8. **No scope drift:** Greenhouse is already implemented; do not rewrite it. Workday remains deferred. Do not start second/third-wave adapters before the first-wave gate is reviewed.
9. **No premature infrastructure:** local-first. No Docker, paid resources, deployment or hosting changes as part of this milestone.

## Checkpoint sequence

Each checkpoint has its own implementation, tests, evidence and review. A checkpoint is not Accepted until the user reviews the evidence.

| Checkpoint | Scope | Exit evidence |
|---|---|---|
| M4-C01 | Investigate Ashby against real employer boards | Verified endpoints, request/response examples, config fields, vacancy fields, completeness behavior, limits and apply URL behavior; investigation report only |
| M4-C02 | Compare Ashby findings with Greenhouse architecture and define the smallest adapter design | File-level design, responsibility boundaries, registry/config changes required, contract mapping and identified differences; no implementation yet |
| M4-C03 | Implement Ashby URL recognition and configuration validation | Supported URL cases, invalid URL cases and registry-driven config tests |
| M4-C04 | Implement Ashby provider retrieval | HTTP client behavior, timeout/error handling, successful/empty/partial outcomes and deterministic fixtures |
| M4-C05 | Implement Ashby response mapping | Stable source ID, title, description, location, timestamps, vacancy URL and application URL mapping tests |
| M4-C06 | Connect Ashby to the shared extraction/persistence workflow | Source can be extracted and persisted through shared services; no duplicate employer/vacancy records |
| M4-C07 | Add Ashby API inspection/onboarding integration | URL detection, source preview and config validation work through the existing API/admin workflow where applicable |
| M4-C08 | Ashby contract, regression and live validation | Unit/contract tests, at least three target-board checks where live boards permit, evidence of completeness and candidate destination validation |
| M4-GATE | Review Ashby and common adapter pattern | User accepts the design/pattern before the next platform begins |
| M4-C09 onward | Repeat the bounded adapter lifecycle for Lever, Teamtailor, Personio, Recruitee and Workable | Each platform has its own investigation, design, implementation, tests and live-validation checkpoints |
| M4-WAVE2 | SmartRecruiters, BambooHR and Breezy HR | Start only after first-wave pattern review; preserve each platform's own evidence and limitations |
| M4-WAVE3 | Simplify.hr, eRecruit/Neptune investigation, Zoho Recruit and SAP SuccessFactors | Investigate per-employer; do not assume a general public API or conflate eRecruit with Graylink Neptune |

### First adapter: Ashby

Use the employer test targets in `docs/ATS-EMPLOYER-TEST-TARGETS.json`: Midnite, MyEdSpace and Tree Traction. These are investigation targets, not proof that every endpoint or field works today.

The investigation must establish:
- How the official Ashby-hosted careers URL identifies the board slug, including supported URL variants and redirects.
- The exact public Job Postings API request and response shape, including whether one request returns the complete published board.
- Whether descriptions are inline and whether any detail request is needed.
- Stable job identity and fields available for title, location, workplace type, department/team, publication/update dates, compensation and application destination.
- How empty boards, malformed payloads, unexpected response shapes, timeouts, throttling and HTTP failures appear.
- Whether the returned job URL is the canonical vacancy page and whether a separate application URL exists.
- Whether the observed behavior is consistent across the three target employers.
- Any restrictions or operational limits. Do not use authenticated/private endpoints or bypass access controls.

## Required first-chat handoff prompt

The next chat must begin with investigation, not coding. Use this instruction:

> We are starting **M4-C01: Ashby adapter investigation** in the Thungatha Scout repository, branch `dev`. Read `AGENTS.md`, `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`, `IMPLEMENTATION-PLAN.md`, this M4 document, `AI-WORKING-GUIDE.md`, `CODING-STANDARDS.md`, `docs/ATS-PLATFORM-RESEARCH.md`, `docs/ATS-EMPLOYER-TEST-TARGETS.json`, and both registries before doing anything.
>
> Investigate Ashby using Midnite, MyEdSpace and Tree Traction. Inspect the actual career pages and public network/API behavior. Prove the request URL, method, parameters, response shape, completeness, fields, stable identifiers, empty/error behavior, and exact vacancy/application URLs. Record reproducible examples and differences between employers. Do not infer behavior from documentation alone when a live request can verify it.
>
> Treat the existing Greenhouse implementation as the architectural reference. Inspect its URL parsing, contracts, HTTP adapter, response mapper, extraction service, API route, registry setup and tests. Explain which boundaries can be reused and which Ashby-specific details require a different implementation. Do not copy Greenhouse blindly and do not create parallel shared pipeline logic.
>
> **This checkpoint is investigation/design only. Do not modify application code, add dependencies, implement the adapter, or start another ATS.** Produce a concise evidence report and a proposed file-by-file design for M4-C02. Explicitly separate provider HTTP, URL/config validation, response mapping, extraction orchestration, persistence and API routing responsibilities.
>
> Enforce the repository rule that every handwritten source-code file and test is at most 100 physical lines. Plan modules around single responsibilities; do not minify or split code artificially. Identify required tests and run no implementation changes. Report unknowns honestly and stop for review.

## Platform order

**First wave:** Ashby, Lever, Teamtailor RSS, Personio XML, Recruitee XML, Workable public widget. Greenhouse remains the implemented reference and is excluded from new adapter work.

**Second wave:** SmartRecruiters, BambooHR, Breezy HR.

**Third wave:** Simplify.hr, eRecruit/Neptune investigation, Zoho Recruit, SAP SuccessFactors.

**Deferred/separate:** Workday is deferred until explicitly reactivated. Placement Partner is a separate recruitment-agency pipeline, not a direct employer ATS. JobAdder remains customer/partner-authorised unless a separate public route is proven. Leaply remains an unconfirmed discovery lead.

## Milestone acceptance

- Each adapter has verified URL recognition, configuration requirements, retrieval method and source evidence.
- Each adapter passes unit and contract tests for normal, empty, malformed, partial and failed retrieval as applicable.
- At least three employer boards are checked where available; exceptions are explicitly documented.
- Stable source-scoped identity, meaningful vacancy fields and exact candidate destinations are proven.
- Shared persistence, quality, deduplication and lifecycle behavior is reused.
- Adding another employer to a supported platform requires registry configuration, not employer-specific adapter code.
- Every handwritten source file remains within 100 physical lines.
- The user reviews each platform gate before the next wave proceeds.
