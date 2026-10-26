# M1 — Employer Discovery and Source Registry

**Status:** In progress (26 October 2026)  
**Outcome:** A traceable registry of candidate employers and official careers sources within Cape Town.  
**Dependency:** M0 — Repository Audit and Scope Lock (Accepted)

## Purpose and scope

Discover employers across industries and company sizes, identify their official careers pages, classify the source relationship, and preserve evidence for verification and review. Company discovery must not be filtered by job title or industry. Companies may be retained even when no current vacancy is found.

## Checkpoint status rules

Use only: **Not started**, **In progress**, **Blocked**, **In review**, **Accepted**. Each checkpoint record includes changes made, commands/tests actually run, observed evidence, unresolved issues, next action and user review status.

## M1-C01 — Discovery inputs and evidence model
**Status:** In progress

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

**Changes made:** M1 activated. M1-C01 selected as the first bounded checkpoint.

**Verification commands/tests actually run:** Repository file retrieval through GitHub connector; no application tests run yet.

**Observed results/evidence:** M0 accepted. Current backend is a scaffold with no domain model or runnable test suite. The local clone attempt failed due to DNS resolution, so implementation must be committed in small reviewable steps and tests run in a working checkout as soon as available.

**Open issues or decisions:** Choose the initial discovery/search mechanism only after the evidence contract is established. Source terms and registry persistence remain later checkpoint decisions.

**Next action:** Implement the discovery candidate/evidence schema and tests for distinct run outcomes.

**Reviewed/accepted by user:** M1 started on user instruction, 26 October 2026; M1-C01 is not yet accepted.
