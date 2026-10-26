# M0 — Repository Audit and Scope Lock

**Status:** Not started  
**Outcome:** A repository-grounded baseline and reviewed scope before further implementation.  
**Dependency:** None

## Purpose and scope

Inspect the actual Scout repository and preserve its history. The existing `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md` is not to be replaced or casually rewritten. It is a historical and decision reference that must be compared with the live code.

## Checkpoint status rules

Use only: **Not started**, **In progress**, **Blocked**, **In review**, **Accepted**.

Every checkpoint record must include changes made, commands/tests actually run, observed evidence, unresolved issues, next action, and user review status. Code written alone does not qualify as acceptance.

## Checkpoints

### M0-C01 — Branch, repository and artifact inventory

**Goal:** establish the actual starting point.

**Work**
- Inspect default branch, known working branch, recent commits and pull requests.
- Inventory source files, tests, scripts, configuration, reports, CSVs and generated artifacts.
- Identify the Greenhouse experiment and any other adapters or utilities already present.
- Record dirty working-tree state if working in a local checkout; do not discard user changes.
- Do not overwrite `backend/data/companies.csv` or historical reports.

**Exit criteria**
- A repository map and branch/commit baseline are recorded.
- Existing data and experimental work are identified.
- No unrelated files or code are changed.

### M0-C02 — Source-of-truth reconciliation

**Goal:** compare established documentation with live implementation without silently changing either.

**Work**
- Compare the source-of-truth document, README, code, tests and report schemas.
- Classify each finding as verified current behavior, historical observation, conflicting documentation, hypothesis or open question.
- Apply the current agreed scope: Cape Town only for initial company discovery; all industries and job types remain eligible during discovery.
- Record any mismatch that requires a decision instead of resolving it by assumption.

**Exit criteria**
- Conflicts and stale statements are listed with evidence.
- The existing source-of-truth file remains unchanged unless the user explicitly approves a documented update.
- Current scope and open decisions are reviewed.

### M0-C03 — Baseline verification

**Goal:** know which existing behaviors work before changes begin.

**Work**
- Identify the project's actual environment/setup instructions and test commands.
- Run the available test suite and relevant CLI smoke tests where practical.
- Record exact commands, exit codes, counts, and important output.
- Distinguish a failed search backend from a successful search with zero results.
- Test a known public Greenhouse board independently if the current code and source allow it.

**Exit criteria**
- A dated baseline report records actual results and limitations.
- Historical test claims are not presented as current results.
- Search failure and true-empty outcomes are separately represented or logged as gaps.

### M0-C04 — Scope and risk review

**Goal:** agree the smallest maintainable implementation path.

**Work**
- Confirm employer-first sourcing and official-careers-page evidence requirements.
- Confirm source categories and how recruitment agencies, staffing companies and hybrid organisations are represented.
- Confirm explicit human approval before publication.
- Review the proposed adapter boundary, internal state storage, Supabase publication boundary, admin access, scheduling and cost constraints.
- List decisions requiring user approval before implementation.

**Exit criteria**
- A reviewed gap list and ordered implementation recommendation exist.
- No new paid service, AI provider, source, or database is approved by implication.
- User has reviewed the audit and agreed the next milestone.

## Progress record

**Changes made:** None recorded yet.

**Verification commands/tests actually run:** None recorded yet. Populate only after execution.

**Observed results/evidence:** Pending live repository inspection.

**Open issues or decisions:** Confirm branch state, existing test baseline, actual adapter inventory, source approval evidence and publication contract.

**Next action:** Complete M0-C01 through M0-C03 against the live repository.

**Reviewed/accepted by user:** No.
