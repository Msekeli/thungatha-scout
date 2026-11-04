# AI Working Guide — Antigravity, Codex and Copilot

**Purpose:** keep AI-assisted work consistent across tools without allowing any tool to invent project decisions or bypass review.

## 1. Shared context

All assistants must use `AGENTS.md` as the repository-wide instruction source and `CHATGPT-PROJECT-GUIDE.md` as the concise current product/architecture brief. The source-of-truth document remains authoritative for dated decisions; older notes are historical when superseded by a later decision record. Before coding, they must also read the source of truth, master implementation plan, and active milestone document. Tool-specific instructions may supplement these rules but must not contradict them.

## 2. How to start a task

Provide the assistant with:

- the milestone/checkpoint ID;
- the intended outcome and acceptance criteria;
- relevant file paths or evidence;
- constraints and decisions that must not change.

Ask it to inspect the repository before proposing edits. For investigation-only tasks, explicitly prohibit code changes. For implementation tasks, require a concise plan before broad or multi-file changes.

## 3. How to execute a checkpoint

For each checkpoint:

1. Confirm the goal, scope and dependencies.
2. Inspect relevant code, tests, branches and working-tree changes.
3. Identify the smallest safe implementation.
4. Implement only the approved scope.
5. Add/update tests.
6. Keep every handwritten source-code file across backend and frontend at 100 physical lines or fewer. The automated line-limit check (`python3 scripts/check-file-line-limits.py`) and naming check (`python3 scripts/check-naming-conventions.py`) enforce this rule. Split by cohesive responsibility.
7. Run tests and quality gates, recording actual results.
8. Review the diff for unrelated edits, secrets and destructive changes.
9. Update the checkpoint record with evidence and unresolved work.
10. Stop for user review where required.

Do not combine multiple checkpoints just because an AI tool can implement them in one prompt. Keep changes reviewable and reversible.

## 4. Tool-specific use

### Google Antigravity

Use the repository-root `AGENTS.md` as the shared project contract; Antigravity automatically discovers it at the workspace/repository root. Keep agent tasks bounded. Review proposed plans, browser actions, terminal commands and diffs before accepting them. Do not allow unattended deployment, destructive data changes or paid-resource provisioning without explicit approval.

### OpenAI Codex

Use `AGENTS.md` as the repository-level instructions. Start with repository inspection and the active checkpoint. Require tests and a final evidence summary. Do not ask Codex to mark work Accepted; acceptance is the user's decision.

### GitHub Copilot

Use the repository-root `AGENTS.md` plus `.github/copilot-instructions.md`. Copilot CLI and supported Copilot agent experiences discover these repository instruction files; IDE support can vary by feature and configuration. For Copilot Chat/agent tasks, name the checkpoint and relevant milestone file. Review generated changes, especially persistence, source-validation, publication and security code. Suggestions or generated tests are not proof until executed.

## 5. AI-generated data and decisions

- Treat AI responses as untrusted input.
- Validate structured output against a schema before use.
- Keep AI behind a small provider interface so Gemini and Groq can be substituted.
- Use deterministic logic for URLs, deduplication, timestamps, state transitions and publication eligibility.
- AI may suggest a company classification or extract candidate fields, but must retain evidence and confidence/uncertainty.
- AI cannot grant source permission, approve an employer, override a human review state, or publish an unapproved vacancy.
- Avoid sending secrets or unnecessary personal data to external AI providers.
- Handle quota exhaustion, timeouts and malformed responses without corrupting existing data.

## 6. Repository naming and file-creation workflow

This section is mandatory for Antigravity, Codex, Copilot and every other assistant. `AGENTS.md` is the rule source; `CODING-STANDARDS.md` gives further guidance. Do not invent a separate naming style for a particular tool.

Before creating or renaming anything:

1. Inspect the current repository tree and relevant source/configuration files.
2. State the responsibility the new directory or file will own.
3. Choose a precise name that communicates that responsibility. Prefer descriptive multi-word names; do not use a generic one-word label for convenience.
4. Apply the naming conventions: kebab-case for ordinary directories/files; snake_case for Python modules and importable packages; exact names only where a framework/tool requires them.
5. For tests, use explicit categories such as `test-suites/unit-tests/`, `test-suites/integration-tests/` and `test-suites/contract-tests/`. Python test modules should use `test_<behavior>.py` names.
6. Check that the path does not duplicate an existing responsibility or repeat information already expressed by its parent directory.
7. If renaming, find and update every import, path reference, test configuration and CI workflow in the same change; then run the relevant checks.
8. Do not create speculative empty folders. If the responsibility or name is unclear, ask the user before creating it.

Examples:

- Good: `backend/test-suites/unit-tests/`, `backend/test-suites/integration-tests/`.
- Avoid: `backend/tests/unit/`, `backend/tests/integration/`.
- Good Python module: `employer_discovery.py`; avoid `utils.py` or `helpers.py` unless that is genuinely the single responsibility and no clearer name exists.
- Good ordinary directory: `operational-diagnostics/`; avoid `diagnostics/` when the narrower responsibility is known.
- A short name is not automatically wrong: keep a precise external platform name such as `greenhouse` when it identifies the platform-specific adapter. Do not expand names just to add words.

## 7. Registry and documentation workflow

Before implementing an ATS/career-site adapter, inspect:

- `backend/registry/ats-adapter-registry.json` for adapter status, retrieval method, capabilities and required configuration;
- `backend/registry/employer-source-registry.json` for employer identity, official careers URLs, source mappings and verification evidence.

Keep generic adapter behavior separate from employer-specific source configuration. Do not add employer identifiers or evidence to adapter definitions, and do not duplicate generic capabilities in employer records. Unknown values remain explicitly unknown; do not infer capabilities from an adapter's name or from a single successful request.

When editing documentation, follow the single-primary-responsibility naming rule in `AGENTS.md`. Update the source of truth for established product decisions, the master plan for milestone-level scope/status, and the active milestone for checkpoint work/evidence. Preserve accepted checkpoint evidence and historical records.

## 8. Prompt template

> Work on **[M#-C##]** only. First read `AGENTS.md`, `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`, `IMPLEMENTATION-PLAN.md`, and the active milestone document. Inspect the current code and working tree before editing. Preserve existing data, reports, and experimental implementations. Do not change unrelated files or make unapproved architecture/source/cost decisions. Implement the smallest safe change, add or update tests, and run the relevant checks. Report exact files changed, commands and observed results, remaining gaps, and the next action. Do not mark the checkpoint Accepted; leave it for user review.

## 9. Human review gates

Explicit user review is required before:

- changing product scope or milestone order;
- adding or approving a production data source;
- changing storage or publishing contracts;
- introducing paid services or materially increasing usage;
- deleting/migrating existing data or reports;
- accepting a milestone or deploying a production change.

## 10. Current vacancy operating model\n\nRoutine human approval of every vacancy is not required. Sources are confirmed by an administrator at onboarding. Vacancies that pass deterministic quality gates are published automatically; hard failures are suppressed and uncertain cases enter the exception queue. AI cannot bypass hard gates or publish directly. Every automated decision must be auditable.\n\n## 11. Do not do this

- Do not rewrite the source of truth to make it agree with newly generated code.
- Do not invent repository state, test results, source permissions or acceptance.
- Do not replace existing implementations before auditing them.
- Do not create abstractions, agents, queues or services without a concrete requirement.
- Do not leave the user with a large unverified diff and claim completion.
