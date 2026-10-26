# M1 — Employer Discovery and Source Registry

**Status:** In progress (26 October 2026)  
**Outcome:** A traceable registry of candidate employers and official careers sources within Cape Town.  
**Dependency:** M0 — Repository Audit and Scope Lock (Accepted)

## Purpose and scope

Discover direct employers across industries and company sizes that have a credible Cape Town connection and an official careers, jobs, vacancies, Join Us, Work With Us or equivalent recruitment page. The page may be company-hosted or an external portal clearly linked from the employer's official website. Do not require an ATS or filter by job title or industry. Exclude recruitment agencies and staffing firms from the direct-employer registry. Companies may qualify even when no current vacancy is found.

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
- Use bounded, reproducible, search-provider-independent queries for careers pages and recruitment entry points.
- Keep Cape Town as the initial geographic scope and record the evidence for the employer's Cape Town connection.
- Discover company-built pages and employer-linked external portals, not only ATS-hosted boards.
- Record search results as leads; do not treat snippets or titles as proof of employer identity or source ownership.
- Avoid treating a single query or search backend as exhaustive.
- Retain discovery run metadata and report coverage limitations.

**Exit criteria**
- Repeatable run produces traceable candidates or a clearly reported incomplete/failure result.
- Discovery records can be reproduced from recorded evidence.
- No unsupported claim of exhaustive coverage is made.

**Implementation progress (26 October 2026)**
- Added a bounded query plan and replaceable search-provider interface in
  `backend/app/application/employer_discovery.py`.
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
- Added offline unit tests with a fake provider. They have not been run by the
  assistant under the agreed workflow; local verification is pending.

**Open issues**
- The current live search provider is unreliable: the latest recorded run failed on 9 of 10 queries. Do not add more DDGS fallback complexity without evidence that it improves distinct, relevant employers found.
- The current research branch contains source investigations and ATS adapters, but no reusable Bing search-provider implementation was identified in the branch files inspected. Do not claim a Bing comparison has been completed.
- The current report is a baseline, not an authoritative registry. Aggregator filtering is intentionally conservative and must be reviewed against new results; official employer ownership, direct-employer classification, Cape Town connection and recruitment-page linkage remain unverified.
- Search snippets do not establish Cape Town presence or official source ownership. The discovery stage must collect candidate recruitment-page URLs; M1-C03 verifies the employer identity, source ownership/linkage and organization classification.
- Results are emitted as JSON to stdout; durable registry persistence and CSV
  reporting remain M1-C04 work.

**Next action:** Pull `dev`, install the updated backend requirements, run the
unit tests and inspect one bounded discovery report. Review provider behavior and
sample candidate evidence before deciding whether to proceed with source
verification in M1-C03.

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

## M1-C04 — Registry persistence and reporting

**Status:** Not started

**Goal:** persist discovery outcomes without losing provenance or damaging existing data.

**Work**
- Choose a persistence/reporting approach consistent with the audited repository.
- Preserve historical JSON/CSV reports and existing company data.
- Make repeated runs idempotent and retain first-seen/last-checked information where appropriate.
- Summarize new, verified, unresolved, failed and unchanged candidates.

**Exit criteria**
- Repeated runs do not create uncontrolled duplicates.
- Reports distinguish candidate counts from verified official sources.
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

**Next action:** Establish a reliable search provider using a bounded comparison, then review a sample of distinct direct employers and their official recruitment pages. M1-C02 remains unaccepted until the discovery yield, evidence quality and failure reporting meet the exit criteria.
