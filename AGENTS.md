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
6. Run the relevant tests and quality checks. Never claim a command passed unless it was actually run.
7. Report changed files, commands/results, evidence, unresolved issues and the next action.
8. Update checkpoint progress records only with verified facts.
9. Stop for user review when a checkpoint requires an explicit product, architecture, source-permission, security or cost decision.

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
