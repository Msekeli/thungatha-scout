# Lever Adapter Investigation — M4-LEVER-A

**Investigation date:** 9 November 2026  
**Checkpoint:** M4-LEVER-A  
**Status:** Accepted — 9 November 2026; M4-LEVER-B integration in progress  
**Scope:** Mama Money, Theodo and Wing Assistant only

## Decision

Lever is a materially simpler integration candidate than Ashby. Lever documents an unauthenticated public Postings API for published vacancies and explicitly states that published postings are publicly viewable and may be scraped by third parties. No partner-feed approval is documented as a prerequisite for reading these published postings.

The public API is suitable for a shared Lever adapter. Live requests from the user's local environment verified all three cohort boards, pagination, stable IDs, vacancy descriptions/fallback, locations and exact job/application URLs. The adapter implementation is committed on `dev`; the user subsequently ran the focused tests and mandatory checks, then directed progression to M4-LEVER-B.

## Official public API contract

Lever's official [Postings API documentation](https://github.com/lever/postings-api) documents:

- List endpoint: `GET https://api.lever.co/v0/postings/{SITE}?skip={N}&limit={N}&mode=json`.
- EU-hosted sites use `https://api.eu.lever.co/v0/postings/{SITE}`; the corresponding hosted careers pages use `jobs.eu.lever.co`.
- The public API returns published postings. Lever states that published postings are publicly viewable and may be scraped by third parties; internal/unlisted, closed and draft postings are not exposed through this public API.
- The response is JSON when `mode=json` or the `Accept: application/json` header is supplied.
- Pagination uses numeric `skip` and `limit` parameters.
- A single posting can be retrieved using `GET /v0/postings/{SITE}/{POSTING-ID}`.

The separate Lever API at `/v1` is authenticated and exposes customer hiring data. Do not use it for Scout's public vacancy ingestion. Do not retrieve internal or unlisted postings.

## Documented public posting fields

The official Postings API schema documents:

| Lever field                                                                | Scout field            | Mapping rule                                                                                                                                                                  |
| -------------------------------------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                                                       | `external_job_id`      | Required stable posting identifier; validate uniqueness across pages.                                                                                                         |
| `text`                                                                     | `title`                | Required job title.                                                                                                                                                           |
| `descriptionPlain`                                                         | `description`          | Prefer complete plain-text description. Preserve raw payload.                                                                                                                 |
| `description`                                                              | raw description        | Styled HTML alternative; preserve as received.                                                                                                                                |
| `categories.location`                                                      | `location_text`        | Primary location.                                                                                                                                                             |
| `categories.allLocations`                                                  | `location_text`        | Preserve multiple locations; define deterministic normalized formatting.                                                                                                      |
| `categories.department` / `team`                                           | `department`           | Map only when populated.                                                                                                                                                      |
| `country`                                                                  | country metadata       | ISO 3166-1 alpha-2 country code; retain in raw payload unless the normalized contract has a matching field.                                                                   |
| `hostedUrl`                                                                | source vacancy URL     | Validate exact posting destination.                                                                                                                                           |
| `applyUrl`                                                                 | `application_url`      | Validate exact vacancy-specific application destination.                                                                                                                      |
| `workplaceType`                                                            | raw/workplace metadata | Values documented as unspecified, on-site, remote or hybrid.                                                                                                                  |
| `salaryRange`, `salaryDescription`                                         | compensation metadata  | Optional; preserve without making it a required field.                                                                                                                        |
| no timestamp in official schema; `createdAt` reported in observed payloads | `published_at`         | Treat `createdAt` as an undocumented candidate field only. Verify presence, units, meaning and consistency across all three live boards before mapping; otherwise leave null. |
| no documented source-update timestamp                                      | `source_updated_at`    | Leave null; do not substitute another timestamp.                                                                                                                              |

The official public list schema documents a unique posting ID and full description fields, but does not list a timestamp field. A recent independent inspection of other Lever boards reports an additional `createdAt` value in milliseconds. This is not part of Lever's published schema and has not been verified against this cohort. Treat it as an observed-but-undocumented candidate field, not a guaranteed contract. No source-update timestamp is documented.

## Employer cohort and board evidence

The repository's target cohort contains these Lever-hosted boards:

| Employer       | Site slug    | Careers board                    | Current board evidence                                                                                         |
| -------------- | ------------ | -------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Mama Money     | `mamamoney`  | https://jobs.lever.co/mamamoney  | Search-indexed board content includes Cape Town roles such as Recon & FinOps Manager and System Administrator. |
| Theodo         | `theodo`     | https://jobs.lever.co/theodo     | Search-indexed board content includes Software Engineer roles in Cape Town under Theodo UK.                    |
| Wing Assistant | `getwingapp` | https://jobs.lever.co/getwingapp | Search-indexed board content includes Cape Town and South Africa remote vacancies.                             |

These observations confirm that the public boards contain vacancy listings and relevant South African/Cape Town examples. They do not establish API response counts, pagination completeness or exact JSON field values.

## Live API verification status

The following requests were attempted:

- `https://api.lever.co/v0/postings/mamamoney?mode=json`
- `https://api.lever.co/v0/postings/theodo?mode=json`
- `https://api.lever.co/v0/postings/getwingapp?mode=json`

The web retrieval environment could not open the three API URLs. A local Python request also failed before receiving an HTTP response because DNS resolution was unavailable. These are research-environment failures, not evidence that Lever's endpoints are down.

No live API response bodies, posting counts, page counts or exact apply URLs were obtained. The actual board pages were discoverable through search results, but that is not a substitute for inspecting the JSON contract against the cohort.

## Live cohort verification — 9 November 2026

The user ran the public API retrieval locally against all three employer boards using `limit=100`, incrementing `skip` until a short page was returned.

| Employer       | Total records | Page sizes        | Unique IDs | Missing IDs | Cape Town matches |
| -------------- | ------------: | ----------------- | ---------: | ----------: | ----------------: |
| Mama Money     |             7 | 7                 |          7 |           0 |                 4 |
| Theodo         |           131 | 100, 31           |        131 |           0 |                 3 |
| Wing Assistant |           375 | 100, 100, 100, 75 |        375 |           0 |                 4 |
| **Total**      |       **513** |                   |    **513** |       **0** |            **11** |

All 513 records had an ID, title, categories, `createdAt` integer, `hostedUrl` and `applyUrl`. All three boards returned a final short page, supporting pagination completion for this observed snapshot. The exact job and application URLs were present in every record.

Description completeness differs by board:

- Mama Money: 7/7 records have non-empty `descriptionPlain`.
- Theodo: 131/131 records have non-empty `descriptionPlain`.
- Wing Assistant: 319/375 records have non-empty `descriptionPlain`; 56 are missing it.

The four Cape Town Wing Assistant matches all have IDs and exact hosted/application URLs. One, **Inside Sales Manager**, has an empty `descriptionPlain`; its list and detail responses both contain a 1,362-character HTML `description`. The other three Cape Town matches have non-empty plain-text descriptions.

All `createdAt` values were integers across the 513 records. This confirms presence and type for this cohort snapshot, but does not independently prove the field's semantic meaning or justify treating it as a source-update timestamp. Keep `source_updated_at` null. Do not map `createdAt` to `published_at` until its meaning is sufficiently established.

The observed workplace types were:

- Mama Money: 6 onsite, 1 remote.
- Theodo: 43 onsite, 88 hybrid.
- Wing Assistant: 341 remote, 24 hybrid, 10 onsite.

**Interpretation:** Lever's public API, pagination, identifiers and posting/application destinations are verified for all three targets. All 11 observed Cape Town vacancies have descriptions either in plain text or HTML. The adapter prefers `descriptionPlain`, falls back to HTML-to-text extraction, and leaves description null only when both are empty. Shared deterministic completeness gates remain authoritative.

## Proposed retrieval and pagination behavior

1. Resolve the site slug and region from the verified employer board URL. The current three targets use `jobs.lever.co`, so the initial expected host is global `api.lever.co`; confirm this from live requests.
2. Request JSON using `mode=json` and a bounded `limit`.
3. Continue with increasing `skip` values until an empty page or a page smaller than the requested limit is returned. If a page is exactly full, request the next page to establish completion.
4. Reject malformed responses and duplicate/missing posting IDs. Do not treat a partial page sequence as a successful complete extraction.
5. Validate `hostedUrl` and `applyUrl` as exact posting-specific destinations. Do not replace them with a generic board URL.
6. The public list includes description fields; use the single-posting endpoint only if live evidence shows that the list payload is incomplete.
7. Inspect whether `createdAt` is present on each cohort board, establish whether it is a Unix-millisecond creation/publication timestamp, and compare it with the public job page. Do not map it until validated. No source-update timestamp is documented.

The official documentation notes that the public API does not support cross-origin requests from unrelated domains. Scout should retrieve through its backend, not directly from a user's browser. Confirm backend request behavior during live validation.

## Implementation delivered in M4-LEVER-A

- `backend/scout/ats_adapters/lever_adapter/lever_source_adapter.py` — shared `ATSAdapterResult` wrapper and lifecycle.
- `backend/scout/ats_adapters/lever_adapter/lever_postings_client.py` — source configuration validation and HTTP client lifecycle.
- `backend/scout/ats_adapters/lever_adapter/lever_pagination.py` — bounded HTTP pagination, duplicate-ID detection and completeness handling.
- `backend/scout/ats_adapters/lever_adapter/lever_postings_contracts.py` and `lever_response_mapper.py` — provider response contract and HTTP failure mapping.
- `backend/scout/ats_adapters/lever_adapter/lever_description_parser.py` — standard-library HTML-to-text fallback preserving paragraph boundaries.
- `backend/scout/ats_adapters/lever_adapter/lever_vacancy_mapper.py` — Lever-to-`NormalizedVacancy` mapping; timestamp fields remain null and raw payload is retained.
- Focused tests under `backend/test-suites/unit-tests/ats-adapters/lever-adapter/` cover description fallback, normalized mapping, pagination, duplicate IDs, empty boards, rate limits and EU host selection.

The adapter requires explicit `slug` and `region` source configuration. Employer-specific slugs are not embedded in adapter code. Registry activation and shared extraction-service registration remain M4-LEVER-B work.

## Description fallback evidence — 9 November 2026

The user checked all four pages of Wing Assistant's board and found exactly one Cape Town vacancy with an empty `descriptionPlain`: **Inside Sales Manager** (`e5932534-4c7c-4117-babb-261420641c48`). Its list response contained an HTML `description` of 1,362 characters. The single-posting endpoint returned `descriptionPlain` length 0 and HTML `description` length 1,362. This establishes that the vacancy description is available as HTML even when the plain-text field is empty; it is not an absent-description record.

The inspected HTML uses ordinary `div`, `p` and `strong` elements plus `&nbsp;` entities. The implementation uses Python's standard-library `HTMLParser`, converts non-breaking spaces, and preserves paragraph/list boundaries as newlines. It prefers non-empty `descriptionPlain`, then falls back to `description`; the original raw payload is retained. It does not fetch detail endpoints for every posting.

## Remaining verification before completing checkpoint A

1. Run the focused Lever unit tests locally.
2. Run the mandatory file line-limit and naming checks.
3. Run the broader backend unit suite and record exact results.
4. Review the diff and confirm all source/test files remain within 100 physical lines.

`createdAt` is present as an integer in all 513 observed records but is not in the official schema and its semantics are not independently established. The adapter deliberately leaves `published_at` and `source_updated_at` null; timestamp uncertainty is not a blocker for this implementation.

## Evidence required to complete investigation

1. Retrieve all three live JSON boards and record HTTP status, page sizes, total observed records, unique IDs, descriptions, locations, country, workplace type, hosted URLs and apply URLs.
2. Test pagination to completion for each board; verify there are no missing or duplicate IDs across pages.
3. Verify the global/EU API host for each employer and validate the exact job and application destinations.
4. Check the undocumented `createdAt` candidate field on all three boards, confirm its units and meaning, and record how absent/invalid values are represented. No source-update timestamp is documented.
5. Compare representative records across all three employers and confirm the same adapter configuration model works for all.

## Verification

- Official Lever Postings API documentation reviewed: https://github.com/lever/postings-api
- Official Lever developer FAQ reviewed: https://hire.lever.co/developer/support — distinguishes public Postings API from the authenticated Lever API.
- Public board pages inspected through indexed results: Mama Money, Theodo and Wing Assistant. Theodo's Cape Town-filtered board exposes Frontend Software Engineer, Full Stack Software Engineer and Senior Full Stack Software Engineer roles; Mama Money's board exposes several Cape Town roles; Wing Assistant's board exposes Cape Town roles.
- Independent third-party sampling reports `createdAt` in milliseconds on other Lever boards. This field is absent from Lever's official public schema and remains unverified for this cohort.
- User-provided local API results: 513 records across the three boards, 513 unique IDs, zero missing IDs, 11 Cape Town matches, and all job/application URLs present.
- Description completeness: Mama Money 7/7 and Theodo 131/131 have non-empty `descriptionPlain`; Wing Assistant has 319/375 non-empty `descriptionPlain`. The remaining 56 have empty plain text; the Cape Town Inside Sales Manager case was verified to have a 1,362-character HTML description in both list and detail responses. Other 55 records' HTML fallback has not yet been sampled.
- The initial external research environment could not retrieve API URLs; this limitation was overcome by local requests from the user's environment.
- Adapter implementation and focused tests committed on `dev`; see implementation commits `bde5d56`, `74043d2`, `385504e`, `f8d6e03`, `5d062d7`, `63e85bdb`, `b5e99e2`, `7222319`, `4e64868`, `32ccfbe`, `c61f14f`, `fdaf57d`, `8665cfd`, `ed0b001`, `640cfb3`, `f12ce29` and `653781e`.
- The implementation is not yet registered in `source_extraction_service.py`; that integration and registry changes belong to M4-LEVER-B.
- No Lever employer-specific records or generic adapter registry entries have been activated.
- Focused Lever tests passed (10 passed in 0.91s); the line-limit check passed; the repository-wide naming check failed with 38 unrelated violations and no Lever adapter paths.

**Checkpoint outcome:** M4-LEVER-A is accepted following user review. M4-LEVER-B is in progress; integration and regression verification remain outstanding.


## M4-LEVER-B integration update — 9 November 2026

The adapter is now registered with the shared extraction service. The generic registry marks Lever as implemented and constrains its `region` configuration to `global` or `eu`. The employer/source registry contains pending configurations for Mama Money (`mamamoney`), Theodo (`theodo`) and Wing Assistant (`getwingapp`); employer identity/source relationship and permission have not been promoted to verified or allowed.

The source create/update API contracts now accept Lever. The backend exposes `/lever/discover` (URL parsing/configuration only) and `/lever/inspect` (bounded public-board retrieval). The frontend Add Company and company source-management flows route supported Lever board URLs to those endpoints and persist the detected slug/region. URL discovery deliberately does not retrieve vacancies; the subsequent background extraction uses the shared persistence pipeline.

B tests added for registry region validation, default factory registration, Lever source API creation, board URL parsing and URL-only discovery. The user must run the broader backend/frontend checks and live API/admin extraction validation before B can be accepted.
