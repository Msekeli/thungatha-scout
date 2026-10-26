# M1 — Employer Discovery and Source Registry

**Status:** Not started  
**Outcome:** A traceable registry of candidate employers and official careers sources within Cape Town.  
**Dependency:** M0 — Repository Audit and Scope Lock (Accepted)

## Purpose and scope

Discover employers across industries and company sizes, identify their official careers pages, classify the source relationship, and preserve evidence for verification and review. Company discovery must not be filtered by job title or industry. Companies may be retained even when no current vacancy is found.

## Checkpoint status rules

Use only: **Not started**, **In progress**, **Blocked**, **In review**, **Accepted**. Each checkpoint record must include changes made, commands/tests actually run, observed evidence, unresolved issues, next action and user review status.

## Checkpoints

### M1-C01 — Discovery inputs and evidence model

**Goal:** define what a candidate and its evidence must contain.

**Work**
- Define stable candidate identity and deduplication behavior.
- Capture discovery query/method, observed URL, timestamp, official careers URL when found, location evidence and evidence references.
- Distinguish unknown identity from a verified identity; never infer company identity from an ATS token alone.
- Define outcomes for successful search with results, successful search with no results, request failure and total discovery failure.

**Exit criteria**
- Candidate/evidence schema is documented and reviewed.
- Unknown and failed states are explicit.
- Tests cover empty results and search failure separately.

### M1-C02 — Cape Town employer discovery

**Goal:** discover candidates without narrowing the employer universe by role or industry.

**Work**
- Use bounded, reproducible discovery queries and inspect result URLs.
- Keep Cape Town as the initial geographic scope.
- Record source evidence rather than relying only on snippets or titles.
- Avoid treating a single query or search backend as exhaustive.
- Retain discovery run metadata and report coverage limitations.

**Exit criteria**
- Repeatable run produces traceable candidates or a clearly reported incomplete/failure result.
- Discovery records can be reproduced from their recorded evidence.
- No unsupported claim of exhaustive coverage is made.

### M1-C03 — Official careers page and source classification

**Goal:** establish whether a candidate's recruitment source is official and identify the relationship.

**Work**
- Verify the employer's own website and careers page where possible.
- Record ATS redirects and the evidence connecting the ATS board to the employer.
- Classify as direct employer, recruitment agency, staffing company, hybrid, other or unresolved.
- Keep ambiguous cases in review rather than guessing.
- Record source access method, usage terms, attribution requirements, quotas and approval status.

**Exit criteria**
- Each verified source has evidence and a classification.
- Unresolved cases remain reviewable.
- Technical accessibility is not mistaken for permission to use data.

### M1-C04 — Registry persistence and reporting

**Goal:** persist discovery outcomes without losing provenance or damaging existing data.

**Work**
- Choose a persistence/reporting approach consistent with the audited repository.
- Preserve historical JSON/CSV reports and the existing `backend/data/companies.csv`.
- Make repeated runs idempotent and retain first-seen/last-checked information where appropriate.
- Produce summaries of new, verified, unresolved, failed and unchanged candidates.

**Exit criteria**
- Repeated runs do not create uncontrolled duplicates.
- Reports distinguish candidate counts from verified official sources.
- Existing data is preserved and schema changes are documented.

### M1-C05 — Verification and review

**Goal:** establish the discovery workflow's reliability.

**Work**
- Test malformed URLs, redirects, duplicate candidates, search backend failure, empty search results and ambiguous identity.
- Review sample records manually against official pages.
- Record representative evidence and known blind spots.
- Obtain explicit user review before accepting the milestone.

**Exit criteria**
- Relevant automated tests pass and commands/results are recorded.
- Sampled records are supported by source evidence.
- Failure states and review queue are usable.
- User explicitly accepts M1.

## Progress record

**Changes made:** None recorded yet.

**Verification commands/tests actually run:** None recorded yet.

**Observed results/evidence:** Pending M0 acceptance and M1 implementation.

**Open issues or decisions:** Search provider choice, source terms, evidence retention, source classification policy and registry persistence should be confirmed based on the M0 audit.

**Next action:** Begin only after M0 is accepted.

**Reviewed/accepted by user:** No.
