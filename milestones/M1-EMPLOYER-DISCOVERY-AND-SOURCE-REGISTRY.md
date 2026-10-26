# M1 — Employer Discovery and Source Registry

**Status:** In progress (26 October 2026)  
**Outcome:** A traceable registry of candidate employers and official careers sources within Cape Town.  
**Dependency:** M0 — Repository Audit and Scope Lock (Accepted)

## Purpose and scope

Discover employers across industries and company sizes, identify their official careers pages, classify the source relationship, and preserve evidence for verification and review. Company discovery must not be filtered by job title or industry. Companies may be retained even when no current vacancy is found.

## Checkpoint status rules

Use only: **Not started**, **In progress**, **Blocked**, **In review**, **Accepted**. Each checkpoint record includes changes made, commands/tests actually run, observed evidence, unresolved issues, next action and user review status.

## M1-C01 — Discovery inputs and evidence model
**Status:** In review

**Goal:** define the candidate/evidence contract and make success-empty distinct from failures.

**Work**
- Define candidate identity and conservative deduplication rules.
- Capture discovery method/query, observed URL, UTC timestamp, official careers URL when verified, location evidence and evidence references.
- Distinguish unknown identity from verified identity; an ATS token alone never proves employer identity.
- Represent successful results, successful empty results, request failure and total discovery failure as separate outcomes.

**Exit criteria**
- Candidate/evidence schema is documented and reviewed.
- Unknown and failure states are explicit.
- Automated tests distinguish empty results from request/discovery failures.

**Checkpoint evidence**
- Added `backend/app/domain/discovery.py` with typed candidate, evidence, identity, organization, review and run-outcome models.
- Added `backend/tests/unit/test_discovery.py` and Pydantic to `backend/requirements.txt`.
- Added `milestones/M1-C01-DISCOVERY-CONTRACT.md`.
- Fixed enum declarations for Python compatibility in commit `8202978` (`Fix discovery enum compatibility`).
- From `backend/`, installed requirements inside a virtual environment using `python -m pip install -r requirements.txt`.
- Ran `python -m unittest discover -s tests/unit -v` after the fix; **10 tests passed, 0 failures**. The user reran the suite after committing and reported `Ran 10 tests ... OK`.
- Pushed commit `8202978` to `origin/dev`.

## M1-C02 — Cape Town employer discovery
**Status:** Not started

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

**Changes made:** Added typed candidate, evidence, identity, organization, review and run-outcome models; added unit tests and Pydantic dependency; documented the C01 contract. Fixed the three enum declarations that referenced undefined `StrEnum` names by using `str, Enum`.

**Verification commands/tests actually run:** From `backend/`, installed dependencies using `python -m pip install -r requirements.txt` in an activated virtual environment. Ran `python -m unittest discover -s tests/unit -v` after the fix and again after committing; all 10 tests passed. `git diff --check` was previously requested but its output was not provided, so it is not recorded as verified. Commit `8202978` was pushed to `origin/dev`.

**Observed results/evidence:** Tests cover successful empty results, non-empty results, request failure, discovery failure, identity validation, timezone validation and stable IDs. The test suite passed locally on Python 3.14.7 with the dependencies installed from `backend/requirements.txt`.

**Open issues or decisions:** The C01 contract is data-model scope only; no discovery provider, source terms/approval workflow, registry persistence, or end-to-end discovery run is implemented by this checkpoint. These belong to later checkpoints. User review of the C01 acceptance criteria is still pending.

**Next action:** Review the C01 contract and test evidence, then explicitly accept C01 or request changes. After acceptance, begin C02 planning.

**Reviewed/accepted by user:** M1 started on user instruction, 26 October 2026. C01 is in review pending explicit user acceptance.
