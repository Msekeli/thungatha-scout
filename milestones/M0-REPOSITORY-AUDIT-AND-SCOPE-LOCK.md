# M0 — Repository Audit and Scope Lock

**Status:** Accepted (26 October 2026)  
**Outcome:** Evidence-based repository baseline and reviewed scope before implementation.  
**Audit report:** [M0 Repository Audit Report](M0-AUDIT-REPORT.md)

## M0-C01 — Branch and artifact inventory
**Status:** Accepted. Inspected `main`, `dev`, `research`, `setup/backend-prototype`, and `feature/cape-town-greenhouse-workday-api`. Recorded branch heads, artifacts, current scaffold, Greenhouse research, Workday client/tests and FastAPI experiment in `M0-AUDIT-REPORT.md`. Research branches were not modified.

## M0-C02 — Source-of-truth reconciliation
**Status:** Accepted. The source-of-truth file supplied in project files has been restored at repository root as `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`. Its rules align with the documented direction: Cape Town only, employer-first sourcing, explicit uncertainty, human approval before publication, replaceable AI providers and bounded operational costs. Proposals remain proposals where validation is still required.

## M0-C03 — Baseline verification
**Status:** Accepted — static baseline established; runtime checks remain unverified.

Observed baseline: `dev` has an Azure Functions Python v2 health entry point and `azure-functions` as its only backend dependency. Unit/integration folders contain placeholders only; the frontend has no `package.json` or runnable build/test configuration. No integrated canonical job model, ATS adapter, persistence layer, admin API or AI provider implementation exists on `dev`.

Checks actually performed: GitHub branch/tree/file retrieval across five branches; source inspection of `backend/function_app.py` and `backend/requirements.txt`; attempted `git clone https://github.com/Msekeli/thungatha-scout.git /tmp/thungatha-scout`, which failed because this environment could not resolve `github.com`.

No pytest, Ruff, Azure Functions host, frontend build, deployed health check or live-source test was run. No runtime/test pass is claimed. Since the scaffold has no runnable application test suite and the checkout could not be cloned here, runtime verification is explicitly carried into implementation work rather than misrepresented as complete.

## M0-C04 — Scope and risk review
**Status:** Accepted. Initial geography is Cape Town only; discovery is not filtered by industry, company size or job title. Official employer careers publication is authoritative; an ATS board alone does not prove employer identity. Failed searches remain distinct from successful empty results. Unknown identity/location/source/vacancy states remain explicit. Human approval is required before publishing; AI cannot approve or publish autonomously. Preserve historical research and do not merge experimental branches wholesale.

Deferred to relevant implementation milestones: Azure region/hosting compatibility, Table Storage access patterns/keys, Supabase schema/stable IDs, admin authentication/deployment and source-specific terms/access.

## Progress record
**Changes:** Added `milestones/M0-AUDIT-REPORT.md`; restored `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`; updated this checkpoint and the master plan.

**Evidence:** GitHub branch and file retrieval succeeded. Source-of-truth content was committed to `dev`. Local clone failed due to DNS/network resolution. No application tests/builds were run.

**Next action:** Start M1 — Employer Discovery and Source Registry. Establish a runnable checkout and add/run targeted tests as behavior is introduced.

**Reviewed/accepted by user:** User requested on 26 October 2026 that M0 be rechecked and closed. This accepts the repository audit and scope baseline, not runtime behavior that has not been tested.
