# AI Working Guide — Antigravity, Codex and Copilot

**Purpose:** keep AI-assisted work consistent across tools without allowing any tool to invent project decisions or bypass review.

## 1. Shared context

All assistants must use `AGENTS.md` as the repository-wide instruction source. Before coding, they must also read the source of truth, master implementation plan, and active milestone document. Tool-specific instructions may supplement these rules but must not contradict them.

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
6. Run tests and quality gates, recording actual results.
7. Review the diff for unrelated edits, secrets and destructive changes.
8. Update the checkpoint record with evidence and unresolved work.
9. Stop for user review where required.

Do not combine multiple checkpoints just because an AI tool can implement them in one prompt. Keep changes reviewable and reversible.

## 4. Tool-specific use

### Google Antigravity
Use `AGENTS.md` as the shared project contract and provide the active checkpoint in the task prompt. Keep agent tasks bounded. Review proposed plans, browser actions, terminal commands and diffs before accepting them. Do not allow unattended deployment, destructive data changes or paid-resource provisioning without explicit approval.

### OpenAI Codex
Use `AGENTS.md` as the repository-level instructions. Start with repository inspection and the active checkpoint. Require tests and a final evidence summary. Do not ask Codex to mark work Accepted; acceptance is the user's decision.

### GitHub Copilot
Use `AGENTS.md` and `.github/copilot-instructions.md`. For Copilot Chat/agent tasks, name the checkpoint and the relevant milestone file. Review generated changes, especially persistence, source-validation, publication and security code. Suggestions or generated tests are not proof until executed.

## 5. AI-generated data and decisions

- Treat AI responses as untrusted input.
- Validate structured output against a schema before use.
- Keep AI behind a small provider interface so Gemini and Groq can be substituted.
- Use deterministic logic for URLs, deduplication, timestamps, state transitions and publication eligibility.
- AI may suggest a company classification or extract candidate fields, but must retain evidence and confidence/uncertainty.
- AI cannot grant source permission, approve an employer, override a human review state, or publish an unapproved vacancy.
- Avoid sending secrets or unnecessary personal data to external AI providers.
- Handle quota exhaustion, timeouts and malformed responses without corrupting existing data.

## 6. Prompt template

> Work on **[M#-C##]** only. First read `AGENTS.md`, `THUNGATHA-SCOUT-SOURCE-OF-TRUTH.md`, `IMPLEMENTATION-PLAN.md`, and the active milestone document. Inspect the current code and working tree before editing. Preserve existing data, reports, and experimental implementations. Do not change unrelated files or make unapproved architecture/source/cost decisions. Implement the smallest safe change, add or update tests, and run the relevant checks. Report exact files changed, commands and observed results, remaining gaps, and the next action. Do not mark the checkpoint Accepted; leave it for user review.

## 7. Human review gates

Explicit user review is required before:
- changing product scope or milestone order;
- adding or approving a production data source;
- changing storage or publishing contracts;
- introducing paid services or materially increasing usage;
- deleting/migrating existing data or reports;
- accepting a milestone or deploying a production change.

## 8. Do not do this

- Do not rewrite the source of truth to make it agree with newly generated code.
- Do not invent repository state, test results, source permissions or acceptance.
- Do not replace existing implementations before auditing them.
- Do not create abstractions, agents, queues or services without a concrete requirement.
- Do not leave the user with a large unverified diff and claim completion.
