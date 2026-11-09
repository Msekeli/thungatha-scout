# Ashby Adapter Investigation — M4-ASHBY-A

**Investigation date:** 9 November 2026  
**Checkpoint:** M4-ASHBY-A  
**Status:** Deferred — partner-feed enquiry sent; awaiting Ashby's response  
**Scope:** Midnite, MyEdSpace and Tree Traction only

## Decision

Do not implement or register the Ashby adapter while partner-feed access and source-use terms remain unresolved. The user has confirmed that an enquiry email was sent to Ashby on 9 November 2026; the team is awaiting a response. The documented public endpoint is technically suitable for a read-only careers-board integration, but live cohort responses and stable vacancy identity remain unverified.

This is an evidence gap, not a conclusion that Ashby is technically unsupported.

## Confirmed official API behavior

Ashby's [Public Job Postings API](https://developers.ashbyhq.com/docs/public-job-posting-api) documents:

- `GET https://api.ashbyhq.com/posting-api/job-board/{JOB_BOARD_NAME}?includeCompensation=true`
- The board name is the final path segment of the employer's hosted Ashby board.
- The response contains an `apiVersion` and `jobs` array.
- Documented job fields include title, location, secondary locations, department, team, workplace type, HTML/plain description, `publishedAt`, employment type, address, `jobUrl`, `applyUrl`, and `isListed`.
- `isListed=false` means the posting is available only by direct link and should not be displayed in the board listing.
- The endpoint is described for an organisation to populate its own careers page. The documentation does not establish pagination, a stable posting ID or a source-updated timestamp in its documented response schema.

The authenticated `jobPosting.list` and `jobPosting.info` endpoints require the `jobsRead` permission. They are not substitutes for the public endpoint and must not be used with employer credentials that Scout does not possess.

Ashby's [Dedicated Partner Job Feeds](https://developers.ashbyhq.com/docs/dedicated-partner-job-feeds) documentation provides a separate, stronger third-party integration contract. Ashby provisions a dedicated JSON or XML feed for a partner; each customer must enable that partner integration in Ashby Admin before its published jobs are shared. The feed is updated hourly and explicitly requires a UUID `id`, `updatedAt`, `publishedAt`, `externalLink`, plain/HTML descriptions and structured locations. This resolves stable identity and update-time mapping for the partner-feed route, but does not grant Scout access: feed provisioning and employer opt-in are prerequisites. Scout's eligibility for this programme has not been established.

## Partner onboarding route

Ashby's official [Integrations](https://www.ashbyhq.com/integrations) page describes a separate prospective integration-partner process:

1. Submit an integration enquiry; Ashby reviews fit and may follow up with questions.
2. If the product is a fit, Ashby schedules an introduction call to understand the product and customer workflow.
3. After validation, the parties complete legal review; Ashby then provides a sandbox and technical support contacts.
4. The partner builds and validates the integration with Ashby's support.
5. The partner demonstrates the end-to-end integration for Ashby's approval before marketplace publication.

Ashby says it prefers prospective partners to have a solution built and ready to provide a seamless customer experience before the introduction stage. This process is not proof that Scout qualifies, nor does it replace the specific request for a dedicated job feed. The practical enquiry should explicitly ask whether a vacancy-ingestion product such as Scout is eligible for the dedicated feed, what permission and customer opt-in terms apply, and whether a sandbox or sample feed can be provided.

## Partner enquiry status

- **Status:** Sent, awaiting response (user-confirmed 9 November 2026).
- **Request:** Confirm Scout's eligibility for a Dedicated Partner Job Feed, partner onboarding requirements, employer opt-in, permitted ingestion/display use, and sample or sandbox access.
- **Decision:** Keep Ashby deferred until Ashby responds. Do not implement against an assumed permission or an unprovisioned partner feed.

## Employer cohort and live verification

The repository identifies these board slugs:

| Employer      | Board slug         | API response  |
| ------------- | ------------------ | ------------- |
| Midnite       | `midnite`          | Not retrieved |
| MyEdSpace     | `myedspacecareers` | Not retrieved |
| Tree Traction | `treetraction`     | Not retrieved |

Direct requests to all three documented API URLs were attempted from the available web and command-line environments. The web requests were inaccessible and the command-line request failed DNS resolution. No response bodies, job counts or individual job records were obtained.

The official Dedicated Partner Job Feed schema specifies `id` as a required UUID and `updatedAt` as required. Those fields belong to the partner feed contract, not the documented public Job Postings API contract. Do not assume the public endpoint returns them.

## Field mapping proposal — pending live evidence

| Ashby field                            | Scout field         | Rule                                                             |
| -------------------------------------- | ------------------- | ---------------------------------------------------------------- |
| `id`                                   | `external_job_id`   | Use only if present, non-empty and stable across repeated reads. |
| `title`                                | `title`             | Required; reject malformed records.                              |
| `descriptionPlain` / `descriptionHtml` | `description`       | Prefer plain text; preserve raw payload.                         |
| `location` and `address`               | `location_text`     | Verify how secondary locations should be represented.            |
| `department` / `team`                  | `department`        | Confirm a deterministic preference.                              |
| `jobUrl`                               | source vacancy URL  | Validate exact destination and URL shape.                        |
| `applyUrl`                             | `application_url`   | Required; validate destination.                                  |
| `publishedAt`                          | `published_at`      | Parse as timezone-aware ISO-8601.                                |
| no documented update timestamp         | `source_updated_at` | Leave null; do not substitute publication time.                  |
| `isListed`                             | listing filter      | Exclude records where explicitly false.                          |

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
2. Await Ashby's response to the partner enquiry already sent. Confirm partner eligibility, feed provisioning, customer opt-in, permitted use and sample/sandbox access.
3. Confirm that each employer's official careers site links to the recorded Ashby board, and preserve that evidence.

## Verification

- Official API documentation reviewed: https://developers.ashbyhq.com/docs/public-job-posting-api
- Official partner-feed documentation reviewed: https://developers.ashbyhq.com/docs/dedicated-partner-job-feeds — confirms required UUID `id`, `updatedAt`, hourly feed updates and per-customer opt-in.
- Official integration-partner process reviewed: https://www.ashbyhq.com/integrations — confirms fit review, introduction, legal review, sandbox/technical support, build, validation and approval steps.
- Clarification: public Job Postings API and Dedicated Partner Job Feed are separate contracts. The latter has stable identity/update fields; it is not currently provisioned for Scout.
- User confirmed partner enquiry email sent on 9 November 2026; response pending.
- Live API calls attempted for all three cohort slugs; no response data was available.
- No adapter code or tests were changed.
- No registry entries were changed.
- No adapter implementation commit was created.

**Checkpoint outcome:** Deferred pending Ashby's partner-feed response and live cohort evidence. M4-ASHBY-B is deferred. The user approved moving to M4-LEVER-A while Ashby remains pending.
