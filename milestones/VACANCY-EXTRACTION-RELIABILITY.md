# Vacancy Extraction Reliability

**Status:** In progress  
**Branch:** `dev`  
**Scope:** Improve deterministic vacancy extraction from the existing employer careers sources. This work does not expand employer discovery, change source approval, or publish records.

## Goal

Retain the existing Playwright primary crawler and use Crawlee only as the fallback. Extract reviewable vacancy candidates from known career-page and ATS URL shapes while preserving evidence when a record cannot safely be extracted.

## Implementation

- Add shared deterministic extraction rules for `/position/<slug>`, `/o/<slug>`, `/jobs/<slug>`, and role-like `/careers/<slug>` routes.
- Use surrounding card context to resolve generic calls to action such as `View Role Details`; reject generic navigation such as Library and Skill Hub.
- Preserve linked vacancy pages, job-description PDFs, mailto links, and visible application email addresses as evidence.
- Inspect at most three linked vacancy detail pages per primary-crawler result; this adds evidence but does not mark a candidate verified.
- Distinguish primary extraction, fallback extraction, email-based recruitment, vacancy evidence without extractable records, successful no-vacancy evidence, blocked/inaccessible pages, and unresolved outcomes.
- Report vacancy-record counts rather than counts of companies with any results.

## Regression coverage

Offline tests cover supported route patterns, generic CTA/card-context title extraction, ATS slug fallback, navigation/PDF rejection, and outcome classification.

## Verification status

**Not yet verified by execution in this environment.** The repository connection can read and update the GitHub branch, but the current execution environment cannot clone the repository or run the Python unit suite. Do not treat this checkpoint as accepted until the user or a runnable development environment executes:

```bash
cd backend
python -m unittest discover -s tests/unit -v
python -m compileall -q diagnostics tests/unit
```

Then rerun the same ten-company primary/fallback diagnostic and compare extracted vacancy records with the preserved snapshots in `backend/storage/datasets/default/`. Preserve those stored captures unchanged.

## Remaining checks

- Confirm existing visible-HTML extraction tests still pass, especially Specno title parsing.
- Verify the stored Sintrex, DVT, Stanchion Payments, BBD and Entelect evidence yields sensible candidates without treating PDFs as vacancy records.
- Verify SovTech navigation links do not become candidates.
- Review live detail-page requests and the generated report before deciding whether further platform-specific adapters are needed.

**Acceptance:** Pending test execution and user review.
