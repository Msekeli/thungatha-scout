# Ashby Adapter Investigation — M4-ASHBY-A

**Investigation date:** 9 November 2026  
**Checkpoint:** M4-ASHBY-A  
**Status:** Blocked — live cohort evidence and source-use permission are not established  
**Scope:** Midnite, MyEdSpace and Tree Traction only

## Decision

Do not implement or register the Ashby adapter yet. The documented public endpoint is technically suitable for a read-only careers-board integration, but this investigation could not verify the three target responses, stable vacancy identity or permission for Scout to ingest and republish the data as a third-party service.

This is an evidence gap, not a conclusion that Ashby is technically unsupported.

## Confirmed official API behavior

Ashby's [Public Job Postings API](https://developers.ashbyhq.com/docs/public-job-posting-api) documents:

- `GET https://api.ashbyhq.com/posting-api/job-board/{JOB_BOARD_NAME}?includeCompensation=true`
- The board name is the final path segment of the employer's hosted Ashby board.
- The response contains an `apiVersion` and `jobs` array.
- Documented job fields include title, location, secondary locations, department, team, workplace type, HTML/plain description, `publishedAt`, employment type, address, `jobUrl`, `applyUrl`, and `isListed`.
- `isListed=false` means the posting is available only by direct link and should not be displayed in the board listing.
- The endpoint is described for an organisation to populate its own careers page. The documentation does not establish pagination or a stable posting ID in its documented response schema.

The authenticated `jobPosting.list` and `jobPosting.info` endpoints require the `jobsRead` permission. They are not substitutes for the public endpoint and must not be used with employer credentials that Scout does not possess.

Ashby separately documents [Dedicated Partner Job Feeds](https://developers.ashbyhq.com/docs/dedicated-partner-job-feeds). Ashby provisions these feeds for partners, and each Ashby customer must opt in to sharing its postings with that partner. This is the clearest documented route for third-party job-feed distribution. Scout's eligibility for this programme has not been established.

## Employer cohort and live verification

The repository identifies these board slugs:

| Employer | Board slug | API response |
| --- | --- | --- |
| Midnite | `midnite` | Not retrieved |
| MyEdSpace | `myedspacecareers` | Not retrieved |
| Tree Traction | `treetraction` | Not retrieved |

Direct requests to all three documented API URLs were attempted from the available web and command-line environments. The web requests were inaccessible and the command-line request failed DNS resolution. No response bodies, job counts or individual job records were obtained.

A secondary technical article reports an `id` field in observed Ashby responses, but that is not sufficient evidence for Scout's three target boards. Do not use that claim as the identity contract without inspecting the actual responses.

## Field mapping proposal — pending live evidence

| Ashby field | Scout field | Rule |
| --- | --- | --- |
| `id` | `external_job_id` | Use only if present, non-empty and stable across repeated reads. |
| `title` | `title` | Required; reject malformed records. |
| `descriptionPlain` / `descriptionHtml` | `description` | Prefer plain text; preserve raw payload. |
| `location` and `address` | `location_text` | Verify how secondary locations should be represented. |
| `department` / `team` | `department` | Confirm a deterministic preference. |
| `jobUrl` | source vacancy URL | Validate exact destination and URL shape. |
| `applyUrl` | `application_url` | Required; validate destination. |
| `publishedAt` | `published_at` | Parse as timezone-aware ISO-8601. |
| no documented update timestamp | `source_updated_at` | Leave null; do not substitute publication time. |
| `isListed` | listing filter | Exclude records where explicitly false. |

Do not derive an ID from a URL path unless the cohort evidence proves the path component is stable and unique. Do not treat a missing ID as a successful normalized vacancy.

## Proposed implementation layout

Only after the evidence and source-use decision are accepted:

- `backend/scout/ats_adapters/ashby_adapter/ashby_source_adapter.py` — adapter contract wrapper and lifecycle.
- `backend/scout/ats_adapters/ashby_adapter/ashby_job_board_client.py` — bounded HTTP request to the documented public endpoint.
- `backend/scout/ats_adapters/ashby_adapter/ashby_response_parser.py` — response shape, listing and required-field validation.
- `backend/scout/ats_adapters/ashby_adapter/ashby_vacancy_mapper.py` — Ashby-to-`NormalizedVacancy` mapping.
- Focused tests under `backend/test-suites/unit-tests/ats-adapters/ashby-adapter/`.

The adapter would register through the existing `SourceExtractionService` factory map. Employer slugs remain in the employer/source registry and must not be hardcoded in adapter code. Shared persistence and lifecycle logic remain unchanged.

## Evidence required to unblock

1. Run the Ashby inspection script previously supplied and provide its output for all three slugs. It must include response status, job count, ID presence/uniqueness, `isListed`, descriptions, locations, publication timestamps, `jobUrl` and `applyUrl`.
2. Establish source-use permission for Scout. Preferred route: contact Ashby about its Dedicated Partner Job Feeds programme and obtain partner onboarding/customer opt-in requirements. Do not infer permission merely because an unauthenticated endpoint responds.
3. Confirm that each employer's official careers site links to the recorded Ashby board, and preserve that evidence.

## Verification

- Official API documentation reviewed: https://developers.ashbyhq.com/docs/public-job-posting-api
- Official partner-feed documentation reviewed: https://developers.ashbyhq.com/docs/dedicated-partner-job-feeds
- Live API calls attempted for all three cohort slugs; no response data was available.
- No adapter code or tests were changed.
- No registry entries were changed.
- No adapter implementation commit was created.

**Checkpoint outcome:** Blocked pending cohort response evidence and source-use permission. Stop here; do not start M4-ASHBY-B.
