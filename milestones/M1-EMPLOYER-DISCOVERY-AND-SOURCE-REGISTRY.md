# M1 — Employer Discovery and Source Registry

**Status:** In progress (26 October 2026)  
**Outcome:** A traceable registry of candidate employers and official careers sources within Cape Town.  
**Dependency:** M0 — Repository Audit and Scope Lock (Accepted)

## Purpose and scope

Discover direct employers across industries and company sizes that have a credible Cape Town connection and an official careers, jobs, vacancies, Join Us, Work With Us or equivalent recruitment page. The page may be company-hosted or an external portal clearly linked from the employer's official website. Do not filter by job title or industry. Exclude recruitment agencies and staffing firms from the direct-employer registry. Companies may qualify even when no current vacancy is found.

Employer discovery has two complementary channels, not competing strategies:

1. **General employer discovery:** identify Cape Town employers and their official recruitment entry points without assuming which ATS they use.
2. **ATS-footprint discovery:** identify candidate employer boards and career portals associated with known recruitment platforms, then trace each candidate back to the employer's own website and verify the Cape Town connection.

ATS-footprint discovery exists to improve employer coverage. It must not replace general employer discovery or turn the registry into a list of ATS boards. One ATS can serve many employers, and one employer may use multiple platforms or brands. Measure unique candidate and verified employers separately from board counts and vacancy counts. A provider returning many vacancies for one employer is not broad employer coverage.

The initial ATS investigation set is Greenhouse, Workday, Lever, Breezy HR, and Ashby. This is a discovery/investigation priority, not a claim that all adapters are implemented or approved. Add providers when evidence shows useful Cape Town employer coverage.

## Checkpoint status rules

Use only: **Not started**, **In progress**, **Blocked**, **In review**, **Accepted**. Each checkpoint record includes changes made, commands/tests actually run, observed evidence, unresolved issues, next action and user review status.

## M1-C01 — Discovery inputs and evidence model

**Status:** Accepted (26 October 2026)

**Goal:** define the candidate/evidence contract and make success-empty distinct from failures.

**Work**

- Define candidate identity and conservative deduplication rules.
- Capture discovery method/query, observed URL, timezone-aware observation time, official careers URL when verified, location evidence and evidence references.
- Distinguish unknown identity from verified identity; an ATS token alone never proves employer identity.
- Represent successful results, successful empty results, request failure and total discovery failure as separate outcomes.

**Exit criteria**

- Candidate/evidence schema is documented and reviewed.
- Unknown and failure states are explicit.
- Automated tests distinguish empty results from request/discovery failures.

**Acceptance evidence**

- Added `backend/app/domain/discovery.py` with typed candidate, evidence, identity, organization, review and run-outcome models.
- Added `backend/tests/unit/test_discovery.py` and Pydantic to `backend/requirements.txt`.
- Added `milestones/M1-C01-DISCOVERY-CONTRACT.md`.
- Fixed enum declarations for Python compatibility in commit `8202978` (`Fix discovery enum compatibility`).
- Installed dependencies in a virtual environment from `backend/` using `python -m pip install -r requirements.txt`.
- Ran `python -m unittest discover -s tests/unit -v` after the fix and again after committing; **10 tests passed, 0 failures** on Python 3.14.7.
- Pushed commit `8202978` to `origin/dev`.
- User explicitly accepted C01 on 26 October 2026.

## M1-C02 — Cape Town employer discovery

**Status:** In progress

**Goal:** discover direct employers and their official recruitment entry points without narrowing the employer universe by role, industry, or ATS provider.

**Work**

- Run two complementary query groups: broad employer/careers discovery and ATS-specific footprint discovery. Keep their provenance and result counts separate.
- Keep Cape Town as the initial geographic scope and record the evidence for the employer's Cape Town connection.
- Discover company-built pages and employer-linked external portals, not only ATS-hosted boards.
- For each investigated ATS, document observable public footprints such as hosted board domains, career-portal domains, embedded widgets, redirect patterns and job URL patterns. Search those footprints for candidate boards; do not assume the ATS provides a public global customer directory.
- Treat third-party ATS board directories, search results, repositories and datasets as unverified lead sources. Record their provider, retrieval date and original URL; independently validate the board and employer before promoting a candidate.
- A board token, tenant/site identifier, subdomain or ATS-hosted job page is a source lead, not proof of the legal employer, its Cape Town presence, or an official relationship.
- Record distinct metrics: raw board leads, validated boards, unique employer candidates, verified direct employers, employers with Cape Town evidence, total vacancies and vacancies per employer. Do not use job volume as a proxy for employer coverage.
- Retain broad employer discovery even when ATS-specific discovery is productive. Avoid treating a single query, directory, ATS or search backend as exhaustive.
- Retain discovery run metadata and report coverage limitations.

**Exit criteria**

- Repeatable run produces traceable candidates or a clearly reported incomplete/failure result.
- Discovery records can be reproduced from recorded evidence.
- No unsupported claim of exhaustive coverage is made.

**Implementation progress (26 October 2026)**

- Added a bounded query plan and replaceable search-provider interface. The
  implementation is now split into focused modules under
  `backend/app/application/discovery_*.py`; `employer_discovery.py` is a small
  compatibility/CLI entry point.
- Reused the DDGS metasearch approach from the research prototype. The live
  report showed that `backend="auto"` returned the ambiguous `No results found.`
  exception for multiple queries. The adapter now tries configured backends
  sequentially and reports all-backend errors as failures rather than claiming
  a successful empty search. Each backend attempt has an 8-second timeout.
- Known job aggregators and search-ad redirect URLs are excluded from the
  employer-candidate queue and counted separately; search titles are retained
  in evidence instead of being promoted to employer names.
- The first live baseline showed 3 queries with results and 7 reported failures.
- The follow-up report `backend/employer-discovery-report-fixed.json` showed 1 query with retained candidates and 9 failed queries. Two URLs remained: an Impact.com careers page and a City of Cape Town public employment resource. The latter is not sufficient evidence of the City's own recruitment page. No verified employer registry was produced by that run.
- User reported that the updated offline suite passed: 22 tests, 0 failures. The assistant has not run these tests.
- The default query plan was changed to eight broad careers-page queries. ATS-specific site queries were removed from discovery because they bias discovery toward known ATS platforms.
- Candidate titles are not promoted to employer names. Official URLs, identity, organization type, Cape Town connection and official recruitment-page relationship remain unverified until checked.
- Duplicate observations merge only on the existing C01 stable observation ID;
  search evidence from each query is retained.
- Query failures, successful empty results, malformed results and partial batch
  failures remain distinguishable in the JSON report.
- Added offline unit tests with a fake provider. The user reported the updated
  suite passed (22 tests, 0 failures); this was not independently run by the assistant.

**Open issues**

- The current live search provider is unreliable: the latest recorded run failed on 9 of 10 queries. Do not add more DDGS fallback complexity without evidence that it improves distinct, relevant employers found.
- No reusable standalone Bing search-provider implementation was found in the inspected research branch. A bounded comparison mode was added to run the same queries independently against the supported DDGS `bing`, `brave`, `duckduckgo` and `mojeek` backends. This compares engine behavior without introducing a separate scraper. The live comparison has not yet been run.
- The current report is a baseline, not an authoritative registry. Aggregator filtering is intentionally conservative and must be reviewed against new results; official employer ownership, direct-employer classification, Cape Town connection and recruitment-page linkage remain unverified.
- Search snippets do not establish Cape Town presence or official source ownership. The discovery stage must collect candidate recruitment-page URLs; M1-C03 verifies the employer identity, source ownership/linkage and organization classification.
- ATS-specific discovery is now an additional channel, not a replacement for broad employer discovery. The earlier removal of ATS-specific queries from the default query plan was intended to avoid biasing the entire discovery process toward known ATS platforms; it must not be interpreted as a prohibition on a separately measured ATS-footprint channel.
- Official Greenhouse Job Board API documentation describes public GET access to a specified board using its board token; it does not document a public endpoint for enumerating all customer boards. The authenticated Harvest API's board-listing capability is not a public employer-discovery endpoint. Breezy's official developer API is documented, and Breezy also offers hosted career portals and an embeddable widget, but the reviewed official documentation does not establish a public global customer directory. Therefore, Scout must discover candidate identifiers through external evidence and validate them, not rely on a nonexistent universal ATS directory.
- Breezy HR is explicitly included in the ATS discovery investigation set. Its hosted career-portal footprint and employer-site widget/links are discovery clues; confirm the employer relationship and current access method before implementing or approving an adapter.
- Results are emitted as JSON to stdout; durable registry persistence and CSV
  reporting remain M1-C04 work.

**Next action:** From `backend/`, run `python -m app.application.employer_discovery --compare-backends --max-results-per-query 8` and save the JSON output for review. The comparison reports per-backend query failures, raw hits, known aggregators excluded and distinct candidate URLs; these are still leads, not verified employer counts. Review candidate URLs for direct-employer relevance and credible official careers/application routes before choosing a default provider. M1-C02 remains unaccepted until the live comparison is useful and repeatable.

## M1-C03 — Official careers page and source classification

**Status:** Not started

**Goal:** verify the candidate employer, Cape Town connection, direct-employer classification and official recruitment-page relationship; identify the source relationship without requiring a particular ATS.

**Work**

- Verify the employer's own website and careers page where possible.
- Record ATS redirects and evidence connecting an ATS board to the employer.
- Classify as direct employer, recruitment agency, staffing company, hybrid, other or unresolved.
- Keep ambiguous cases in review rather than guessing.
- Record source access method, usage terms, attribution requirements, quotas and approval status.

**Exit criteria**

- Each verified source has evidence and a classification.
- Unresolved cases remain reviewable.
- Technical accessibility is not mistaken for permission to use data.

## Registry file responsibilities

The initial JSON registry is organized by independently maintained concept:

- `backend/registry/ats-adapter-registry.json`: generic adapter definitions, implementation status, retrieval method, capability metadata, required configuration fields and adapter-level notes.
- `backend/registry/employer-source-registry.json`: employer/organization records, official careers entry points, source mappings, employer-specific adapter configuration and verification evidence.

The first file must not accumulate employer-specific board mappings. The second must not duplicate generic adapter capabilities. Registry contents are provisional until their records and claim-specific evidence are reviewed. A verified source mapping does not by itself verify Cape Town presence, source permission, adapter readiness or human approval.

## M1-C04 — Registry persistence and reporting

**Status:** Not started

**Goal:** persist discovery outcomes without losing provenance or damaging existing data.

**Work**

- Define and validate the contracts for the two registry files; reject malformed records, unknown adapter references and missing required configuration.
- Keep adapter definitions separate from employer/source mappings and claim-specific verification evidence.
- Choose a persistence/reporting approach consistent with the audited repository.
- Preserve historical JSON/CSV reports and existing company data.
- Make repeated runs idempotent and retain first-seen/last-checked information where appropriate.
- Ensure registry updates preserve evidence history and do not promote pending claims to verified without review.
- Summarize new, verified, unresolved, failed and unchanged candidates.

**Exit criteria**

- Repeated runs do not create uncontrolled duplicates.
- Reports distinguish candidate counts from verified official sources.
- Registry records pass schema/contract validation and cross-reference valid adapter keys.
- Generic adapter definitions and employer-specific source mappings remain separate.
- Existing data is preserved and schema changes are documented.

## M1-C05 — Verification and review

**Status:** Not started

**Goal:** establish the discovery workflow's reliability.

**Work**

- Test malformed URLs, redirects, duplicate candidates, search backend failure, empty results and ambiguous identity.
- Review sample records manually against official pages.
- Record representative evidence and known blind spots.
- Obtain explicit user review before accepting M1.

**Exit criteria**

- Relevant automated tests pass and commands/results are recorded.
- Sampled records are supported by source evidence.
- Failure states and review queue are usable.
- User explicitly accepts M1.

## Progress record

**C01 changes:** Added typed candidate, evidence, identity, organization, review and
run-outcome models; added unit tests and Pydantic; documented the C01 contract.
Fixed enum declarations that referenced undefined `StrEnum` names by using
`str, Enum`.

**C01 verification history:** Dependencies were installed from `backend/` using
`python -m pip install -r requirements.txt`. The command
`python -m unittest discover -s tests/unit -v` was run after the enum fix and
again after commit `8202978`; all 10 tests passed on Python 3.14.7.
`git diff --check` was not confirmed and is not recorded as verified.

**Current status:** C01 was explicitly accepted by the user on 26 October 2026.
C02 remains in progress. The user reported 22 unit tests passing after the latest implementation fix. The latest recorded live report is still poor (1 query with retained candidates, 9 failed queries) and does not establish a useful, verified employer set. The default queries now target official careers-page discovery rather than ATS-specific domains. The assistant has not run tests or a live search.

**Next action:** Establish a reliable search provider using a bounded comparison and add a separately reported ATS-footprint discovery experiment for Greenhouse, Workday, Lever, Breezy HR and Ashby. Compare unique employer yield—not just board or job totals—and review a sample of distinct direct employers and their official recruitment pages. M1-C02 remains unaccepted until discovery yield, evidence quality and failure reporting meet the exit criteria.

## ATS discovery evidence and limitations (3 November 2026)

The following findings inform the discovery approach; they do not claim adapter implementation or source approval:

- Greenhouse's public Job Board API accepts a specific `board_token` to retrieve that board's jobs. Its documentation does not describe a public global customer/board enumeration endpoint: https://docs.greenhouse.io/job-board
- Greenhouse's Harvest API documents listing job boards, but it is a customer recruiting-data API rather than an unauthenticated public directory: https://harvestdocs.greenhouse.io/reference/get_v3-job-boards
- Breezy provides official developer API documentation and hosted career portals/widgets. The reviewed documentation does not establish a public global directory of Breezy customers: https://developer.breezy.hr/reference/overview and https://breezy.hr/attract
- Public ATS directories and search-engine indexes can be useful lead sources, but they are third-party evidence. Validate every candidate board against the employer's official web presence and retain source provenance.

**Discovery rule:** Scout must not wait for an ATS vendor to provide a customer directory. It should discover candidate employer/board pairs from multiple independent public footprints, verify each pair, and keep broad employer discovery running in parallel.

## Registry data baseline (3 November 2026)

Two initial JSON files have been added under `backend/registry/`:

- `ats-adapter-registry.json` contains the current adapter catalogue and its known retrieval metadata.
- `employer-source-registry.json` contains initial employer/source candidates, source mappings and separate verification states.

This is a registry data baseline only. It does not complete C04. The files still require an explicit schema/contract, validation tests, a reviewed persistence/update lifecycle and evidence review of their individual records. Existing `candidate` and `pending_verification` values must not be upgraded based on assumptions. C04 remains Not started until its work and exit criteria are completed and verified.

## Scope clarification — v1 delivery sequencing (3 November 2026)

The product's first implementation slice is now explicitly focused on registering and extracting from known Greenhouse and Workday employer boards supplied by the administrator. This is a delivery-sequencing decision; it does not erase or invalidate the C01/C02 discovery research above.

- The broad employer-discovery experiment and ATS-footprint discovery remain useful work, but they are not a dependency for starting the first registration/extraction vertical slice.
- The v1 admin can add an employer by pasting a known Greenhouse or Workday careers/board URL. The backend detects the platform where possible, supports manual selection/override, extracts employer metadata where reliable, and requires administrator confirmation.
- Greenhouse and Workday are the only v1 adapter commitments. Lever, Breezy HR and Ashby remain future investigation candidates, not current implementation scope.
- A supplied ATS board URL is a source lead. Employer identity, official source relationship, Cape Town relevance, source terms/permission and human approval remain separate verification claims.
- The registry's generic adapter definitions remain separate from employer-specific source configuration. Newly added employers using a supported adapter must not require employer-specific adapter code.
- M1 remains In progress. Existing checkpoint status and historical reports are preserved. Do not mark M1 Accepted or rewrite old evidence because the implementation sequence changed.
- Immediate implementation begins with M2 in IMPLEMENTATION-PLAN.md. Revisit remaining M1 discovery work after the first Greenhouse and Workday registration/extraction workflows provide a working baseline.

**Next action:** preserve the discovery experiment and continue implementation through M2/M3/M4. The first live compatibility tests are a Greenhouse board and https://myhcm.wd3.myworkdayjobs.com/digioutsource.
