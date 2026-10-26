# M0 — Repository Audit and Scope Lock

**Status:** Blocked  
**Outcome:** An evidence-based repository baseline and reviewed scope before further implementation.  
**Dependency:** None  
**Audit report:** [M0 Repository Audit Report](M0-AUDIT-REPORT.md)

## Purpose and scope

Inspect the actual Scout repository and preserve its history. The repository instructions require `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md` to be read and reconciled with live code. It was not found in the inspected branch trees. Do not replace or casually rewrite it. This missing authority is a blocker for full M0 acceptance.

## Checkpoint status rules

Use only: **Not started**, **In progress**, **Blocked**, **In review**, **Accepted**.

Every checkpoint record must include changes made, commands/tests actually run, observed evidence, unresolved issues, next action, and user review status. Code written alone does not qualify for acceptance.

## Checkpoints

### M0-C01 — Branch, repository and artifact inventory

**Status:** In review

**Goal:** establish the actual starting point.

**Work completed**
- Inspected `main`, `dev`, `research`, `setup/backend-prototype`, and `feature/cape-town-greenhouse-workday-api` tree heads and relevant paths.
- Recorded branch heads, tracked-path counts, current scaffold, Greenhouse reports/registries, Workday client/tests, and FastAPI experiment in `M0-AUDIT-REPORT.md`.
- Confirmed no source-of-truth file or `backend/data/companies.csv` in the inspected branch trees.
- No research branch was modified.

**Exit assessment:** Inventory recorded; pending user review.

### M0-C02 — Source-of-truth reconciliation

**Status:** Blocked

**Goal:** compare established documentation with live implementation without silently changing either.

**Observed evidence**
- Current instructions require `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`.
- The named file was not found on any of the five inspected branch trees.
- `main-aim.txt` and `ARCHITECTURE-AND-TECHNOLOGY.md` were supplied in project context, but their authority relative to the missing historical document is not established.
- Confirmed current principles and unresolved differences are recorded in the audit report.

**Exit assessment:** Cannot be accepted until the missing source-of-truth is restored or the user explicitly approves a documented authority change.

### M0-C03 — Baseline verification

**Status:** Blocked

**Goal:** know which existing behaviors work before changes begin.

**Commands/results**
- `git clone https://github.com/Msekeli/thungatha-scout.git /tmp/thungatha-scout` — failed: environment could not resolve `github.com`.
- No pytest, Ruff, Azure Functions host, frontend build, or live-source command was run.
- `dev` has no tests beyond placeholders, so no current automated test baseline exists.
- Historical test sources were inspected through GitHub retrieval but were not executed.

**Exit assessment:** Not met. No test pass is claimed.

### M0-C04 — Scope and risk review

**Status:** In review

**Confirmed from current documents**
- Employer-first sourcing; official careers publication is the authority.
- Cape Town is the initial geographic scope; company discovery is not industry- or job-title-filtered.
- Unknown identity, location and source permission remain explicit unresolved states.
- Failed searches must not be reported as successful empty searches.
- Human approval is required before publishing; AI cannot approve or publish autonomously.
- Keep the current one-Function-App proposal and provider/adapter abstraction small; validate hosting, persistence and integration decisions before implementing them.

**Open decisions**
- Restore/identify the required source-of-truth document or explicitly approve an alternative authority arrangement.
- Establish a runnable local environment and execute a real baseline.
- Review Azure region/hosting compatibility, Table Storage access patterns/keys, Supabase schema/stable IDs, admin authentication/deployment, and source-specific terms/access.
- Review the audit report and agree the next milestone only after the blocking issues are resolved.

## Progress record

**Changes made:** Added `milestones/M0-AUDIT-REPORT.md` and updated this checkpoint record with verified repository evidence.

**Verification commands/tests actually run:** GitHub tree/file retrieval for five branches; local clone attempt failed due DNS/network resolution. No application tests or builds were run.

**Observed results/evidence:** See [M0-AUDIT-REPORT.md](M0-AUDIT-REPORT.md). Current `dev` is a scaffold; historical Greenhouse and Workday experiments remain on separate branches.

**Open issues or decisions:** Missing required source-of-truth document; executable baseline unavailable; scope/platform/source questions remain for review.

**Next action:** Restore/resolve the source-of-truth authority and run the baseline in a working checkout. Then review M0 findings before proceeding.

**Reviewed/accepted by user:** No.
