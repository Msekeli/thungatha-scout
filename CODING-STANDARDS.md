# Thungatha Scout — Coding Standards

**Status:** Proposed baseline for review. These standards do not claim that the current repository already complies.

## General

- Prefer clear, maintainable code over cleverness or speculative abstraction.
- Keep source-specific behavior behind a small adapter contract.
- Keep discovery, validation, extraction, normalization, deduplication, approval and publishing responsibilities distinct.
- Use stable identifiers and explicit state values; avoid magic strings scattered through the code.
- Use UTC, timezone-aware timestamps for persisted event times.
- Validate external data at system boundaries.
- Make failure states observable and preserve enough source evidence to explain decisions.
- Avoid unrelated formatting and large rewrites.

## Python

- Use type hints for public functions and important data structures.
- Use Pydantic or equivalent validation at external-data boundaries where it adds value.
- Use Ruff for linting/formatting if confirmed by the repository setup; target an 88-character line length unless existing tooling establishes another standard.
- Prefer small, single-purpose functions. As a guideline, aim for 10–30 lines and review functions exceeding roughly 40 lines; do not split code artificially to meet a number.
- As a guideline, keep modules focused and review modules growing beyond 200–300 lines for cohesive extraction opportunities.
- Use explicit exceptions and structured error reporting; do not swallow errors silently.
- Add pytest coverage for normal, empty, malformed, duplicate, timeout, provider-failure and retry cases as applicable.

## TypeScript / React admin UI

- Use TypeScript strictness and explicit types for API contracts.
- Keep components focused; separate data access, validation and presentation where useful.
- Use accessible labels, keyboard navigation, visible loading/empty/error states and responsive layouts.
- Validate forms and API responses at boundaries where needed.
- Follow the repository's existing formatter/linter configuration rather than adding competing tools.
- Add unit/component tests for meaningful behavior and Playwright tests for critical user flows.

## Adapters and external services

- Define a common input/output contract and explicit capability/limitation metadata.
- Keep credentials server-side and load them from environment configuration or managed identity.
- Apply bounded timeouts, retries and response-size limits.
- Distinguish not-found, empty, blocked, rate-limited, malformed and transient failure outcomes.
- Preserve original source URL, employer careers URL where verified, source identifiers and retrieval timestamps.
- Do not bypass source restrictions or treat technical access as legal/operational approval.

## AI provider integrations

- Encapsulate Gemini and Groq behind a small provider interface.
- Request structured output where supported and validate it before use.
- Keep deterministic processing outside the model.
- Bound retries, tokens, latency and spend; handle rate limits and provider outages.
- Do not send secrets or unnecessary personal information.
- Record model/provider metadata where useful without logging sensitive prompts or credentials.
- AI recommendations cannot replace source evidence or human approval.

## Tests and acceptance

- Tests must be repeatable and avoid depending on live websites unless explicitly classified as integration/smoke tests.
- Mock external providers for unit tests.
- Test that failed extraction cannot mark a vacancy closed and unapproved data cannot be published.
- Record commands actually run and observed results in the relevant checkpoint.
- A passing unit suite alone does not prove source permission, live integration, security or user acceptance.
