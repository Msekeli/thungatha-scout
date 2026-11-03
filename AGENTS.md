# Instructions for AI Coding Agents

These instructions apply to Antigravity, OpenAI Codex, GitHub Copilot and other coding assistants working in this repository.

## Authority and reading order

Before making changes, read:

1. `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md` — established decisions and historical evidence.
2. `IMPLEMENTATION-PLAN.md` — current milestone roadmap and status.
3. The active milestone document under `milestones/`.
4. Relevant code, tests, configuration and reports.
5. `AI-WORKING-GUIDE.md` and `CODING-STANDARDS.md`.

The source-of-truth document must not be overwritten or silently reconciled with new assumptions. If the live code disagrees with documentation, inspect the code/tests and report the discrepancy.

## Required working method

1. State the current milestone/checkpoint and its goal before implementation.
2. Inspect relevant files and the working tree first.
3. Make the smallest change that meets the agreed checkpoint.
4. Preserve existing experimental Greenhouse work, historical reports, company data and user changes.
5. Add or update tests for changed behavior.
6. Keep every Python module directly in `backend/app/application/` at 100 lines or fewer. The automated line-limit test is a required quality gate. Do not evade it by minifying code; split by responsibility. If a larger module appears necessary, stop and request explicit review.
7. Run the relevant tests and quality checks. Never claim a command passed unless it was actually run.
8. Report changed files, commands/results, evidence, unresolved issues and the next action.
9. Update checkpoint progress records only with verified facts.
10. Stop for user review when a checkpoint requires an explicit product, architecture, source-permission, security or cost decision.

## Non-negotiable product rules

- Scout supplies trusted employer-sourced vacancies to Thungatha; it is not a public job-search frontend.
- The employer's official careers publication is the source authority. An ATS is an access mechanism, not proof of employer identity by itself.
- Initial geographic scope is Cape Town only.
- Company discovery includes all industries and company sizes; do not apply job-title filters during discovery.
- Preserve unresolved identity, source classification and location states rather than guessing.
- Search failure must not be reported as a successful search with zero results.
- Human approval is an explicit backend state. AI cannot approve a source or publish records by itself.
- Do not bypass authentication, access controls, robots/terms restrictions or source quotas.
- Do not overwrite `backend/data/companies.csv` or historical reports without an explicitly reviewed migration/change.
- Publishing must be validated and idempotent; unapproved records must not reach Thungatha.
- Avoid adding infrastructure or dependencies without a demonstrated requirement and user review.

## Directory and file naming — mandatory for every contributor and AI tool

This is a repository-wide rule for developers and AI coding agents, including Antigravity, Codex and Copilot. Follow it before creating, moving or renaming any directory or file. `CODING-STANDARDS.md` contains the detailed examples; this section is the mandatory workflow.

- Names must tell a reader what the directory or file is responsible for. A reader must not need to open it or inspect sibling names to guess its purpose.
- Prefer precise, descriptive names made from the fewest words that fully express the responsibility. Do not default to short generic labels. One-word names are allowed only when no clear descriptive alternative exists or a tool/framework mandates the exact name.
- Use kebab-case for ordinary directory names and non-Python filenames. Use snake_case for Python modules and importable package directories because Python imports require it. Preserve exact framework/tool-required names only when the tool actually requires them.
- Do not create vague labels such as `unit`, `integration`, `common`, `shared`, `misc`, `helpers`, `utils`, `lib`, `temp`, `api`, `types` or `data` when a more precise name is possible.
- Test categories must be explicit: use `test-suites/unit-tests/`, `test-suites/integration-tests/`, and `test-suites/contract-tests/` when those categories exist. Never create `tests/unit/` or `tests/integration/`.
- Python test filenames follow Python discovery conventions (for example, `test_employer_discovery.py`); their names must still identify the behavior under test.
- Before creating a file or directory, inspect the current tree and relevant tooling. Check for an existing owner of the responsibility, avoid duplicate/nested names that repeat the parent, and confirm the proposed name is accurate.
- Before renaming an existing path, search all imports, references, configuration, test discovery and CI workflows. Update every reference in the same change and run the affected checks. Do not rename framework-required paths casually.
- Do not create empty placeholder directories for speculative future features. Create a directory when its responsibility and near-term contents are understood.
- If the right name or responsibility is unclear, stop and ask rather than inventing a folder. Explain the proposed name and what belongs inside it.
- When reviewing existing names, distinguish a required convention from a vague scaffold placeholder. Do not rename a folder merely to satisfy a mechanical word-count rule.

## File and registry responsibilities

- Every file must have one clearly defined primary responsibility. Do not combine unrelated concerns merely to reduce the number of files.
- File names must describe that responsibility clearly and specifically. Split independently maintained concepts when necessary, but avoid unnecessary fragmentation and excessively long names.
- The adapter definitions belong in `backend/registry/ats-adapter-registry.json`. This file describes adapter identity, implementation status, retrieval method, capabilities, configuration requirements and adapter-level constraints.
- Employer/source mappings belong in `backend/registry/employer-source-registry.json`. This file describes organizations, official careers entry points, source-to-employer relationships, adapter configuration and verification evidence.
- Do not put employer-specific board identifiers or employer verification evidence in the adapter registry. Do not put generic adapter capabilities in individual employer records.
- Before implementing or changing an adapter, inspect the adapter registry and relevant employer/source mappings. Do not hardcode employer-specific configuration in adapter code.
- Treat registry entries as data requiring validation. A registry status or a populated field is not, by itself, proof of source permission, Cape Town eligibility, implementation readiness or human approval.

## Security and cost

- Never commit secrets, credentials, tokens, private keys or real environment files.
- Never expose backend secrets or Supabase service-role credentials to frontend code.
- Validate all external and AI-generated data before persistence.
- Use bounded timeouts, retries, batch sizes, browser runs and AI calls.
- Do not provision paid resources or trigger costly recurring workloads without approval.
- Log enough for diagnosis, but do not log secrets or unnecessary personal data.

## Documentation discipline

- Keep implementation details in code and the appropriate milestone records.
- Record decisions with rationale and evidence; do not turn a hypothesis into a decision.
- Do not mark a checkpoint Accepted without tests/evidence and explicit user acceptance.
- Do not generate a new competing source-of-truth document.
- Do not reformat or rewrite unrelated files.
- If a task is ambiguous, ask a focused question before making a consequential assumption.

## Completion response

At the end of a task, provide:
- **Checkpoint:** identifier and status.
- **Changes:** files and behavior changed.
- **Verification:** exact commands and observed results.
- **Evidence/gaps:** what remains unverified.
- **Next action:** one clear recommendation.
- **Review needed:** the explicit decision or acceptance requested from the user.
