# M1 — Employer Discovery and Source Registry

**Status:** In progress (26 October 2026)  
**Outcome:** A traceable registry of candidate employers and official careers sources within Cape Town.  
**Dependency:** M0 — Repository Audit and Scope Lock (Accepted)

## Purpose and scope

Discover employers across industries and company sizes, identify their official careers pages, classify the source relationship, and preserve evidence for verification and review. Company discovery must not be filtered by job title or industry. Companies may be retained even when no current vacancy is found.

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

**Goal:** discover candidates without narrowing the employer universe by role or industry.

**Work**
- Use bounded, reproducible discovery queries and inspect result URLs.
- Keep Cape Town as the initial geographic scope.
- Record source evidence rather than relying only on snippets or titles.
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
- The current committed baseline report showed 3 queries with results and 7
  reported failures; those results included multiple job aggregators. The fix
  has been added but still requires local unit tests and a new live report.
- Candidate titles are not promoted to employer names. Official URLs, identity,
  organization type and Cape Town location remain unresolved until verified.
- Duplicate observations merge only on the existing C01 stable observation ID;
  search evidence from each query is retained.
- Query failures, successful empty results, malformed results and partial batch
  failures remain distinguishable in the JSON report.
- Added offline unit tests with a fake provider. They have not been run by the
  assistant under the agreed workflow; local verification is pending.

**Open issues**
- DDGS is an unaffiliated metasearch library; backend availability, terms and
  operational suitability still need review. Backend fallback is not proof that
  the provider is reliable or that a failed query was truly empty.
- The current report is a baseline, not an authoritative registry. Aggregator
  filtering is intentionally conservative and must be reviewed against new
  results; official employer ownership and Cape Town presence remain unverified.
- Search snippets do not establish Cape Town presence or official source ownership.
  M1-C03 must verify those claims against employer-owned pages.
- Results are emitted as JSON to stdout; durable registry persistence and CSV
  reporting remain M1-C04 work.

**Next action:** Pull `dev`, install the updated backend requirements, run the
unit tests and inspect one bounded discovery report. Review provider behavior and
sample candidate evidence before deciding whether to proceed with source
verification in M1-C03.

## M1-C03 — Official careers page and source classification

**Status:** Not started

**Goal:** establish whether a candidate's recruitment source is official and identify the relationship.

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
C02 implementation is in progress. No tests or builds have been run by the
assistant for C02; local verification and review are pending.

**Next action:** User pulls `dev`, runs the backend unit tests, and reviews one
bounded discovery run. M1-C02 remains unaccepted until evidence and user review
support its exit criteria.
