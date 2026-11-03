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

## Directory and file naming

- Directory and file names must communicate their actual responsibility without requiring readers to infer meaning from surrounding folders.
- Prefer specific, descriptive, multi-word names joined with kebab-case. Do not create vague one-word names when a clear descriptive name is available.
- Use a one-word name only when there is no clear, precise multi-word alternative, or when an external framework/tool requires that exact name. A familiar convention is not, by itself, a reason to keep an ambiguous name.
- Avoid generic names such as `common`, `shared`, `misc`, `helpers`, `utils`, `lib`, `temp` and unexplained abbreviations. Replace them with the responsibility they contain.
- Name test directories by the complete test category: `unit-tests`, `integration-tests`, `contract-tests` or another precise category. Do not use nested generic labels such as `tests/unit` or `tests/integration`.
- Before creating a directory or file, check whether its name states what it contains or does, whether its parent already communicates the same information, and whether it duplicates an existing responsibility.
- Do not rename framework-required paths without checking their tooling impact. For Python importable packages, use descriptive `snake_case` names; for other directories and files, use descriptive `kebab-case` names. When a scaffold directory has no implementation yet, resolve its name before adding code to it.
- When reviewing existing names, distinguish intentional conventions from ambiguous placeholders. Do not rename a folder merely to satisfy a mechanical word-count rule.

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
