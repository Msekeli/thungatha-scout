# Thungatha Scout — Coding Standards

**Status:** Proposed baseline for review. These standards do not claim that the current repository already complies.

## Directory and file naming

- Use descriptive kebab-case names for directories and files. A name must communicate the actual responsibility or contents.
- Prefer multi-word names when they make the responsibility clearer. One-word names are permitted only for precise, established technical conventions, proper names, or cases with no clear descriptive alternative.
- Do not use vague convenience names such as `common`, `shared`, `misc`, `helpers`, `utils`, `lib` or unexplained abbreviations. Name the actual responsibility instead.
- Name test groupings explicitly: `unit-tests`, `integration-tests`, `contract-tests`, etc. Avoid `tests/unit` and `tests/integration`.
- Do not create directories just because a future feature may need them. Create a directory when its responsibility and contents are understood.
- Preserve framework- or tooling-required names when they have a precise established meaning. Check imports, test discovery, build configuration and CI paths before renaming an existing directory.
- Review each directory in context. A technically familiar name is not automatically clear; prefer the name that best describes what the directory actually owns.

## General

- Prefer clear, maintainable code over cleverness or speculative abstraction.
- Keep source-specific behavior behind a small adapter contract.
- Keep discovery, validation, extraction, normalization, deduplication, approval and publishing responsibilities distinct.
- Use stable identifiers and explicit state values; avoid magic strings scattered through the code.
- Use UTC, timezone-aware timestamps for persisted event times.
- Validate external data at system boundaries.
- Make failure states observable and preserve enough source evidence to explain decisions.
- Avoid unrelated formatting and large rewrites.

## Registry data

- Keep generic ATS/career-site adapter definitions in `backend/registry/ats-adapter-registry.json`.
- Keep employer identities, official careers entry points, source mappings and claim-specific evidence in `backend/registry/employer-source-registry.json`.
- Each file has one primary responsibility. Do not duplicate adapter capabilities across employer records or employer-specific configuration across adapter definitions.
- Validate registry JSON against an explicit schema/contract before application use. JSON syntax validity alone is insufficient.
- Reject unknown adapter references and missing required configuration fields. Do not silently substitute defaults for required employer-specific identifiers.
- Use explicit, documented status values. Preserve unknown or unverified values as null or an explicit pending state; never manufacture verification dates or evidence.
- Treat employer identity, Cape Town presence, official source relationship, technical retrieval capability, source permission and human approval as separate claims/states.
- Registry edits require tests for valid records, malformed data, unknown adapters, missing configuration, invalid status values and unresolved verification state, as applicable.
- Do not hardcode employer-specific board slugs, tenant/site identifiers or source URLs in adapter implementation when they belong in the employer/source registry.

## Python

- Use type hints for public functions and important data structures.
- Use Pydantic or equivalent validation at external-data boundaries where it adds value.
- Use Ruff for linting/formatting if confirmed by the repository setup; target an 88-character line length unless existing tooling establishes another standard.
- Prefer small, single-purpose functions. As a guideline, aim for 10–30 lines and review functions exceeding roughly 40 lines; do not split code artificially to meet a number.
- Hard limit: every Python module directly in `backend/app/application/` must be 100 lines or fewer, counting blank lines. Split by cohesive responsibility; do not compress or obscure code merely to meet the limit. If a module needs more than 100 lines, stop and ask for explicit review before expanding it. Test files may exceed 100 lines when their cases remain cohesive.
- Enforce this limit with an automated unit test. Run the full unit suite after code changes and before reporting completion.
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
