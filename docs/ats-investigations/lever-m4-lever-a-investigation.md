# Lever Adapter Investigation — M4-LEVER-A

**Investigation date:** 9 November 2026  
**Checkpoint:** M4-LEVER-A  
**Status:** Live cohort verification completed; Wing Assistant description fallback still under investigation  
**Scope:** Mama Money, Theodo and Wing Assistant only

## Decision

Lever is a materially simpler integration candidate than Ashby. Lever documents an unauthenticated public Postings API for published vacancies and explicitly states that published postings are publicly viewable and may be scraped by third parties. No partner-feed approval is documented as a prerequisite for reading these published postings.

Do not implement yet. The API contract and employer boards are identified, but the live JSON responses for all three cohort members could not be retrieved from the available research environment. Confirm actual pagination, payload completeness, descriptions and vacancy/application destinations before implementation.

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

| Employer | Total records | Page sizes | Unique IDs | Missing IDs | Cape Town matches |
| --- | ---: | --- | ---: | ---: | ---: |
| Mama Money | 7 | 7 | 7 | 0 | 4 |
| Theodo | 131 | 100, 31 | 131 | 0 | 3 |
| Wing Assistant | 375 | 100, 100, 100, 75 | 375 | 0 | 4 |
| **Total** | **513** | | **513** | **0** | **11** |

All 513 records had an ID, title, categories, `createdAt` integer, `hostedUrl` and `applyUrl`. All three boards returned a final short page, supporting pagination completion for this observed snapshot. The exact job and application URLs were present in every record.

Description completeness differs by board:
- Mama Money: 7/7 records have non-empty `descriptionPlain`.
- Theodo: 131/131 records have non-empty `descriptionPlain`.
- Wing Assistant: 319/375 records have non-empty `descriptionPlain`; 56 are missing it.

The four Cape Town Wing Assistant matches all have IDs and exact hosted/application URLs. One, **Inside Sales Manager**, has an empty `descriptionPlain`. The other three Cape Town matches have non-empty descriptions. We have not yet checked whether Wing's `description` HTML field or the single-posting endpoint supplies the missing content.

All `createdAt` values were integers across the 513 records. This confirms presence and type for this cohort snapshot, but does not independently prove the field's semantic meaning or justify treating it as a source-update timestamp. Keep `source_updated_at` null. Do not map `createdAt` to `published_at` until its meaning is sufficiently established.

The observed workplace types were:
- Mama Money: 6 onsite, 1 remote.
- Theodo: 43 onsite, 88 hybrid.
- Wing Assistant: 341 remote, 24 hybrid, 10 onsite.

**Interpretation:** Lever's public API, pagination, identifiers and posting/application destinations are verified for all three targets. Theodo and Mama Money meet the observed description-completeness requirement. Wing Assistant needs a deliberate missing-description strategy. Missing descriptions must be represented as incomplete and must never be silently treated as complete or published through a bypass of Scout's completeness gates.

## Proposed retrieval and pagination behavior

1. Resolve the site slug and region from the verified employer board URL. The current three targets use `jobs.lever.co`, so the initial expected host is global `api.lever.co`; confirm this from live requests.
2. Request JSON using `mode=json` and a bounded `limit`.
3. Continue with increasing `skip` values until an empty page or a page smaller than the requested limit is returned. If a page is exactly full, request the next page to establish completion.
4. Reject malformed responses and duplicate/missing posting IDs. Do not treat a partial page sequence as a successful complete extraction.
5. Validate `hostedUrl` and `applyUrl` as exact posting-specific destinations. Do not replace them with a generic board URL.
6. The public list includes description fields; use the single-posting endpoint only if live evidence shows that the list payload is incomplete.
7. Inspect whether `createdAt` is present on each cohort board, establish whether it is a Unix-millisecond creation/publication timestamp, and compare it with the public job page. Do not map it until validated. No source-update timestamp is documented.

The official documentation notes that the public API does not support cross-origin requests from unrelated domains. Scout should retrieve through its backend, not directly from a user's browser. Confirm backend request behavior during live validation.

## Proposed implementation layout

After the three-board live contract is verified:

- `backend/scout/ats_adapters/lever_adapter/lever_source_adapter.py` — adapter contract wrapper and lifecycle.
- `backend/scout/ats_adapters/lever_adapter/lever_postings_client.py` — bounded HTTP retrieval and pagination.
- `backend/scout/ats_adapters/lever_adapter/lever_response_parser.py` — response validation and page-completeness handling.
- `backend/scout/ats_adapters/lever_adapter/lever_vacancy_mapper.py` — Lever-to-`NormalizedVacancy` mapping.
- Focused tests under `backend/test-suites/unit-tests/ats-adapters/lever-adapter/`.

Register the generic Lever adapter definition and employer-specific site slugs/regions in their existing registries only after A is implemented and reviewed. Do not hardcode employer identifiers in adapter code. Reuse the shared extraction and persistence workflow.

## Remaining evidence before adapter implementation

1. For Wing Assistant's 56 records with empty `descriptionPlain`, inspect whether the HTML `description` field is populated. Probe the single-posting endpoint for representative missing-description records, including the Cape Town **Inside Sales Manager** posting.
2. Establish whether the detail endpoint reliably supplies a description for these records. If it does not, the adapter must preserve them as incomplete; do not infer descriptions from titles or external search snippets.
3. Verify `createdAt` semantics before mapping it to `published_at`. It is an observed integer field, not documented in the official schema. Keep `source_updated_at` null.
4. Then implement and test the adapter against the shared contract, including pagination completeness, duplicate/missing IDs, description fallback, exact destinations and incomplete-record handling.

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
- Description completeness: Mama Money 7/7; Theodo 131/131; Wing Assistant 319/375. Wing's 56 missing `descriptionPlain` values require HTML/detail-endpoint investigation.
- The initial external research environment could not retrieve API URLs; this limitation was overcome by local requests from the user's environment.
- No adapter code or tests have been changed.
- No registry entries for Lever have been changed.
- No implementation commit has been created.

**Checkpoint outcome:** Live public API access and pagination are verified for all three targets. M4-LEVER-A remains open only for Wing Assistant description fallback and timestamp semantics. Implementation is not yet authorised by the evidence until those points are resolved.
