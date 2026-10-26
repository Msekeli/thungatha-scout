# Thungatha Scout — Master Implementation Plan

**Document status:** Active roadmap; M0 accepted  
**Purpose:** Master roadmap, milestone scope, dependencies, progress and acceptance tracking  
**Product:** Thungatha Scout  
**Parent product:** Thungatha  
**Repository:** https://github.com/Msekeli/thungatha-scout

## 1. Purpose

This document defines milestone order, scope, dependencies, high-level outcomes, status and completion criteria. Detailed checkpoint definitions, verification evidence, unresolved issues and user-review records belong in the corresponding files under `milestones/`.

`THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md` remains the source of truth for Scout's established decisions and historical observations. Do not replace it with this roadmap. Record conflicts for review rather than silently rewriting either document.

## 2. Product boundary

Thungatha is the user-facing job-search and career-management platform. Scout discovers employers' official careers pages, uses supported career-site/ATS adapters to retrieve vacancies, validates and normalises records, tracks evidence and freshness, and makes approved records available to Thungatha through a defined integration contract.

An ATS is a possible access mechanism; the employer's official careers publication is the source authority. An aggregator listing alone is insufficient evidence of an official employer source.

Initial geographic scope: **Cape Town only**. Do not expand to the whole Western Cape or other cities without an explicit decision.

## 3. Delivery principles

- Inspect current repository, branches, tests and experimental Greenhouse work before implementation.
- Preserve existing data, reports and working code unless a reviewed change explicitly authorises otherwise.
- Prefer a small adapter contract and deterministic processing over a framework-heavy architecture.
- Keep discovery, source validation, extraction, normalisation, deduplication, approval and publishing distinct.
- Make uncertainty visible; do not infer employer identity, source permission, job location or vacancy validity without evidence.
- Human approval is explicit backend state; AI cannot approve or publish by itself.
- Keep Azure usage and AI calls bounded and observable.
- Record only tests and commands actually run; code presence is not proof it works.
- No milestone is accepted without evidence and explicit user review.

## 4. Milestone roadmap

| Milestone | Name | Status |
|---|---|---|
| M0 | Repository Audit and Scope Lock | Accepted |
| M1 | Employer Discovery and Source Registry | Not started |
| M2 | Adapter Contract and Greenhouse Baseline | Not started |
| M3 | Additional Career-Site/ATS Adapters | Not started |
| M4 | Vacancy Normalisation, Deduplication and Freshness | Not started |
| M5 | Review and Approval Workflow | Not started |
| M6 | Thungatha Publishing Integration | Not started |
| M7 | Scheduling, Observability and Recovery | Not started |
| M8 | Admin Operations, Security and Release Acceptance | Not started |

Existing Greenhouse experiments may provide evidence toward a milestone, but do not automatically satisfy its acceptance criteria.

## 5. Milestone summaries

### M0 — Repository Audit and Scope Lock
**Status:** Accepted (26 October 2026). The branch/artifact inventory and scope review are documented in `milestones/M0-AUDIT-REPORT.md`. The required source-of-truth document has been restored to the repository. The current scaffold has no runnable application test suite or frontend build configuration, and runtime checks were not run because this environment could not clone GitHub. These limitations are explicit; no runtime/test pass is claimed. Establish executable tests and a runnable checkout during the first implementation work.

### M1 — Employer Discovery and Source Registry
**Outcome:** A repeatable discovery workflow records candidate employers, official careers pages, source evidence, geography, source type and review status without inventing identities or treating failed searches as empty results.

### M2 — Adapter Contract and Greenhouse Baseline
**Outcome:** A documented adapter interface and a verified Greenhouse implementation provide a stable baseline without discarding existing experimental work.

### M3 — Additional Career-Site/ATS Adapters
**Outcome:** Additional adapters can be added independently behind the shared contract. Each source is evaluated separately for access, terms, data quality and operational limits before production approval.

### M4 — Vacancy Normalisation, Deduplication and Freshness
**Outcome:** Source records become consistent vacancy records with traceable provenance, conservative deduplication, repeatable updates and explicit freshness/availability states.

### M5 — Review and Approval Workflow
**Outcome:** An administrator can inspect ambiguous employers, sources, vacancies and errors; approval is recorded as an explicit backend state with audit evidence.

### M6 — Thungatha Publishing Integration
**Outcome:** Approved, validated records are published idempotently through a documented contract. Unapproved or failed records cannot leak into the public feed.

### M7 — Scheduling, Observability and Recovery
**Outcome:** Discovery, verification, extraction and reconciliation run on bounded schedules, with retries, failure visibility, safe recovery and cost controls.

### M8 — Admin Operations, Security and Release Acceptance
**Outcome:** The minimum operational interface, authentication/authorization, secrets handling, tests, deployment configuration, cost checks and user acceptance are complete.

## 6. Status rules

Use only: **Not started**, **In progress**, **Blocked**, **In review**, **Accepted**. Acceptance requires evidence, actual checks/results, documented remaining gaps and explicit user review. If no runnable tests or runtime environment exist, record that limitation and assign follow-up work; never claim unrun checks passed.

## 7. Change control

1. Do not silently change milestone sequence, approved scope or established source-of-truth decisions.
2. Record the reason and evidence for proposed changes.
3. Update the milestone record and this plan only after the change is agreed.
4. Distinguish observed fact, hypothesis, decision and open question.
5. Preserve prior evidence; correct it with dated clarification rather than erasing history.
6. Do not mark a milestone accepted merely because code has been refactored or files moved.

## 8. Current focus

M0 is accepted as the repository audit and scope baseline. The runtime limitation is recorded rather than hidden. Proceed to M1 — Employer Discovery and Source Registry, beginning with establishing a runnable checkout and adding/running focused tests as behavior is introduced. Validate platform, storage, integration, authentication and source-access decisions before implementation.
