# Lever Adapter Investigation — M4-LEVER-A

**Investigation date:** 9 November 2026  
**Checkpoint:** M4-LEVER-A  
**Status:** Investigation in progress — public contract confirmed; live API payloads not yet retrieved  
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

| Lever field                           | Scout field            | Mapping rule                                                                                                |
| ------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------- |
| `id`                                  | `external_job_id`      | Required stable posting identifier; validate uniqueness across pages.                                       |
| `text`                                | `title`                | Required job title.                                                                                         |
| `descriptionPlain`                    | `description`          | Prefer complete plain-text description. Preserve raw payload.                                               |
| `description`                         | raw description        | Styled HTML alternative; preserve as received.                                                              |
| `categories.location`                 | `location_text`        | Primary location.                                                                                           |
| `categories.allLocations`             | `location_text`        | Preserve multiple locations; define deterministic normalized formatting.                                    |
| `categories.department` / `team`      | `department`           | Map only when populated.                                                                                    |
| `country`                             | country metadata       | ISO 3166-1 alpha-2 country code; retain in raw payload unless the normalized contract has a matching field. |
| `hostedUrl`                           | source vacancy URL     | Validate exact posting destination.                                                                         |
| `applyUrl`                            | `application_url`      | Validate exact vacancy-specific application destination.                                                    |
| `workplaceType`                       | raw/workplace metadata | Values documented as unspecified, on-site, remote or hybrid.                                                |
| `salaryRange`, `salaryDescription`    | compensation metadata  | Optional; preserve without making it a required field.                                                      |
| no documented publication timestamp   | `published_at`         | Leave null; do not infer a date from search indexing or page appearance.                                    |
| no documented source-update timestamp | `source_updated_at`    | Leave null; do not substitute another timestamp.                                                            |

The public list schema documents a unique posting ID and full description fields, but it does not document publication or source-update timestamps. Do not invent either value.

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

## Proposed retrieval and pagination behavior

1. Resolve the site slug and region from the verified employer board URL. The current three targets use `jobs.lever.co`, so the initial expected host is global `api.lever.co`; confirm this from live requests.
2. Request JSON using `mode=json` and a bounded `limit`.
3. Continue with increasing `skip` values until an empty page or a page smaller than the requested limit is returned. If a page is exactly full, request the next page to establish completion.
4. Reject malformed responses and duplicate/missing posting IDs. Do not treat a partial page sequence as a successful complete extraction.
5. Validate `hostedUrl` and `applyUrl` as exact posting-specific destinations. Do not replace them with a generic board URL.
6. The public list includes description fields; use the single-posting endpoint only if live evidence shows that the list payload is incomplete.
7. Record the absence of publication/update timestamps explicitly. Do not infer freshness from page order or external search indexing.

The official documentation notes that the public API does not support cross-origin requests from unrelated domains. Scout should retrieve through its backend, not directly from a user's browser. Confirm backend request behavior during live validation.

## Proposed implementation layout

After the three-board live contract is verified:

- `backend/scout/ats_adapters/lever_adapter/lever_source_adapter.py` — adapter contract wrapper and lifecycle.
- `backend/scout/ats_adapters/lever_adapter/lever_postings_client.py` — bounded HTTP retrieval and pagination.
- `backend/scout/ats_adapters/lever_adapter/lever_response_parser.py` — response validation and page-completeness handling.
- `backend/scout/ats_adapters/lever_adapter/lever_vacancy_mapper.py` — Lever-to-`NormalizedVacancy` mapping.
- Focused tests under `backend/test-suites/unit-tests/ats-adapters/lever-adapter/`.

Register the generic Lever adapter definition and employer-specific site slugs/regions in their existing registries only after A is implemented and reviewed. Do not hardcode employer identifiers in adapter code. Reuse the shared extraction and persistence workflow.

## Evidence required to complete investigation

1. Retrieve all three live JSON boards and record HTTP status, page sizes, total observed records, unique IDs, descriptions, locations, country, workplace type, hosted URLs and apply URLs.
2. Test pagination to completion for each board; verify there are no missing or duplicate IDs across pages.
3. Verify the global/EU API host for each employer and validate the exact job and application destinations.
4. Record how missing publication and source-update timestamps are represented in normalized records.
5. Compare representative records across all three employers and confirm the same adapter configuration model works for all.

## Verification

- Official Lever Postings API documentation reviewed: https://github.com/lever/postings-api
- Official Lever developer FAQ reviewed: https://hire.lever.co/developer/support — distinguishes public Postings API from the authenticated Lever API.
- Public board pages inspected through indexed results: Mama Money, Theodo and Wing Assistant.
- Live API requests attempted for all three site slugs; no HTTP responses were received because the research environments could not resolve/access the API hosts.
- No adapter code or tests were changed.
- No registry entries for Lever were changed.
- No implementation commit was created.

**Checkpoint outcome:** M4-LEVER-A remains in investigation. Public third-party retrieval is documented and does not appear to require partner approval, but live cohort payloads and completeness must be verified before implementation.
