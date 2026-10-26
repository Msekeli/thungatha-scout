# M0 Repository Audit Report

**Audit date:** 26 October 2026  
**Branch:** `dev`  
**Status:** Accepted for repository audit and scope baseline; runtime execution remains unverified.  
**Scope:** Branch/artifact inventory, source-of-truth reconciliation, and current implementation baseline. No research branch was modified.

## 1. Executive summary

The current `dev` branch is an implementation scaffold, not the previous research implementation. It contains an Azure Functions Python v2 health endpoint, package placeholders, a frontend folder skeleton, and project guidance. It does not contain a canonical job model, integrated ATS adapter, persistence layer, admin API, AI provider implementation, or application tests.

The `research` branch retains Greenhouse discovery/analysis reports, company/source registries, URL investigations, a Workday client and tests. `setup/backend-prototype` contains Greenhouse discovery/analysis modules and related tests. `feature/cape-town-greenhouse-workday-api` contains Workday code/tests and a previous FastAPI jobs API experiment. These are distinct historical implementations and were not copied wholesale into `dev`.

The source-of-truth file supplied in the project files was restored at repository root as `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`. Its product rules align with the documented direction. Architecture and hosting choices described as proposals remain proposals.

## 2. Branch and artifact inventory

| Branch | Head observed during audit | Tracked paths observed | Relevant evidence |
|---|---|---:|---|
| `dev` | `35d0954a1823c3ea3f45807224e88a97fd04ea98` | 64 | Scaffold, health endpoint, package/test placeholders |
| `main` | `d86368fe485d61eda66254fed83c7fc9d7679326` | 18 | Earlier baseline |
| `research` | `a10a40088407890d7c86ce0e1cc9818596956807` | 106 | Workday client/tests, Greenhouse reports/registries, URL investigations |
| `setup/backend-prototype` | `a91dced88a556479cbc91b9bb95127b3e860092c` | 31 | Greenhouse source modules and tests |
| `feature/cape-town-greenhouse-workday-api` | `8d8274bd90e063f095321a44aa9db846f32fd747` | 17 | Workday code/tests and FastAPI API experiment |

Counts represent tree entries returned during inspection, not only source files. These branch heads/counts are the audit snapshot; the source-of-truth restoration commit is newer.

## 3. Current `dev` baseline

- Backend: Azure Functions Python v2 entry point and `azure-functions` as the only declared backend dependency.
- Health route: anonymous GET route named `health`, returning JSON. Source-inspected only; not invoked locally or deployed.
- Backend domain/application/adapters/storage/publishing/AI packages are placeholders rather than integrated implementations.
- Unit/integration test folders contain `.gitkeep` placeholders; no runnable application test suite is tracked.
- Frontend has a folder skeleton but no `package.json`, application entry point or runnable build/test configuration.
- `backend/data/companies.csv` was not present in inspected branch trees. Research data was preserved and is not treated as a substitute.

## 4. Research preservation findings

### Greenhouse
The `research` branch contains dated discovery snapshots, board registries, company registries, a consolidated jobs report, a role-relevance report and URL investigations. Prior saved evidence reports 3,582 saved job records across 77 board entries; per-board totals exceed the capped saved-record count, so this is not a complete census. These artifacts are historical evidence, not current vacancy availability or proof of employer identity.

### Workday and API experiment
The `research` and `feature/cape-town-greenhouse-workday-api` branches contain a Workday public CXS client and mocked tests. The feature branch also contains a FastAPI-based jobs API. Since the proposed backend is Azure Functions Python v2, the FastAPI experiment remains historical evidence unless separately reviewed.

No research branch was modified; reports, registries, snapshots, investigations and experimental source were not deleted or regenerated.

## 5. Source and scope reconciliation

The restored source-of-truth and repository guidance establish:
- Scout is the trusted employer-sourced ingestion component, not a duplicate public job-search frontend.
- The employer's official careers publication is authoritative; an ATS is an access mechanism.
- Initial scope is Cape Town only; discovery is not filtered by industry, company size or job title.
- Companies may be retained with zero current vacancies when approval evidence is satisfied.
- Unknown identity, source classification, location and vacancy lifecycle remain explicit states.
- Failed searches differ from successful empty searches; timeouts/outages do not immediately expire vacancies.
- Human approval is explicit backend state; AI cannot independently approve or publish records.
- Gemini and Groq are replaceable provider options; deterministic operations remain deterministic.
- Azure Functions Python v2, a separate React/TypeScript/Vite admin frontend, Azure Table Storage and Supabase are the proposed direction. Platform and integration choices still require validation where specified.

## 6. Verification and limitations

**Checks performed:**
- GitHub branch/tree/file retrieval across `main`, `dev`, `research`, `setup/backend-prototype`, and `feature/cape-town-greenhouse-workday-api`.
- Source inspection of `backend/function_app.py`, `backend/requirements.txt`, and repository guidance.
- Attempted `git clone https://github.com/Msekeli/thungatha-scout.git /tmp/thungatha-scout`; it failed because this environment could not resolve `github.com`.

**Not run:** pytest, Ruff, Azure Functions host, frontend build, deployed health check, or live-source tests. Historical tests were inspected through GitHub retrieval but not executed.

**Interpretation:** The audit establishes that the scaffold has no runnable application test suite or frontend build configuration, and the health route was only inspected as source. No runtime/test pass is claimed. A runnable checkout and targeted test/build configuration must be established as implementation begins.

## 7. Risks and deferred decisions

1. No automated application tests or runnable frontend build currently exist.
2. Runtime health behavior has not been invoked locally or deployed.
3. Greenhouse and Workday research is not integrated behind a shared contract.
4. Historical board tokens and snapshots do not establish employer identity, source permission or current vacancy status.
5. Azure region/hosting compatibility, Table Storage access patterns/keys, Supabase schema/stable identifiers, admin authentication/deployment, and source-specific access/terms require validation in relevant implementation milestones.

These are recorded as implementation risks and follow-up work, not blockers to accepting the repository inventory and scope baseline.

## 8. M0 conclusion

M0 is accepted for the purpose it was defined to serve: repository and research inventory documented, source-of-truth restored, scope and safety rules reconciled, and the unverified baseline explicitly recorded without claiming test success.

**Next milestone:** M1 — Employer Discovery and Source Registry. Establish a runnable checkout and executable tests as part of the first implementation work; preserve research artifacts until selectively reviewed.
