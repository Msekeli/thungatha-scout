# ATS and Career Platform Research — South Africa

**Research date:** 8 November 2026  
**Purpose:** Prioritise employer vacancy-source adapters for Thungatha Scout without excluding employers merely because their ATS is less convenient.

## Executive decision

Implement the easy, public-feed adapters first. Keep all researched platforms in the registry, including difficult, undocumented and partner-dependent sources. A platform being difficult does not mean its employers should be excluded: it means Scout may need a different retrieval strategy or a manual source workflow.

The ranking below estimates implementation effort for one reusable adapter after a valid employer careers URL is known. It does not measure how many South African employers use the platform. A live HTTP 200 is not sufficient acceptance: Scout must retrieve meaningful published vacancies, descriptions where available, stable identifiers and a usable job/application destination.

## Ranked implementation order

| Rank | Platform           | Retrieval pattern                                        | Access                                                      | Difficulty                | Recommended action                               |
| ---: | ------------------ | -------------------------------------------------------- | ----------------------------------------------------------- | ------------------------- | ------------------------------------------------ |
|    1 | Ashby              | Public JSON Job Postings API                             | Unauthenticated, documented                                 | Easy                      | Implement early                                  |
|    2 | Lever              | Public JSON Postings API                                 | Unauthenticated, documented                                 | Easy                      | Implement early                                  |
|    3 | Teamtailor         | RSS/XML at `/jobs.rss`                                   | Public, documented                                          | Easy                      | Implement early                                  |
|    4 | Personio           | XML feed at `/xml?language=en`                           | Public, documented, employer must enable                    | Easy                      | Add to the scope                                 |
|    5 | Recruitee          | Public XML offer feed                                    | Public feed; Careers Site API requires token                | Easy–moderate             | Implement XML, not token API                     |
|    6 | Workable           | Public careers widget JSON endpoint                      | Observed public, undocumented                               | Easy–moderate             | Validate then implement                          |
|    7 | Greenhouse         | Public JSON Job Board API                                | Unauthenticated, documented                                 | Easy; already implemented | Preserve as reference                            |
|    8 | SmartRecruiters    | Public Posting API                                       | Officially public; listing/detail calls                     | Moderate                  | Implement after a live endpoint test             |
|    9 | BambooHR           | Public careers list + per-job detail endpoints           | Observed public, undocumented                               | Moderate                  | Implement after employer-board validation        |
|   10 | Breezy HR          | Public JSON list + HTML detail page                      | List is public/undocumented; details uncertain              | Moderate–hard             | Validate detail extraction first                 |
|   11 | Zoho Recruit       | Public careers HTML with embedded data                   | Undocumented page behavior                                  | Hard                      | Build only against verified real boards          |
|   12 | Workday            | Public careers CXS POST + detail GET                     | Observed public, undocumented                               | Hard                      | Implement after easy adapters                    |
|   13 | SAP SuccessFactors | Tenant-specific Career Site Builder / XML / HTML         | Varies by tenant; legacy XML response retiring              | Hard                      | Do not rely on legacy RSS/XML                    |
|   14 | Simplify.hr        | South African hosted careers pages                       | No general public endpoint verified                         | Hard                      | Inspect actual page/network calls                |
|   15 | Neptune / eRecruit | Employer-specific portal and possible custom integration | No general public feed/API verified                         | Hard                      | Treat as employer-specific investigation         |
|   16 | Placement Partner  | Agency vacancy pages and candidate redirects             | Public pages; identifiers and link behavior need validation | Hard                      | Keep separate agency pipeline                    |
|   17 | JobAdder           | Customer API / possible agency widgets                   | OAuth2 customer authorization                               | Partner-dependent         | Do not build a global API adapter without access |
|   18 | Leaply             | Recruitment engine / marketplace                         | No public vacancy feed verified                             | Not yet an ATS adapter    | Keep as discovery lead, investigate separately   |

Difficulty is an engineering estimate based on documented retrieval method, request shape, pagination, field completeness, detail-page requirements and configuration variance. It is not a vendor quality rating.

## Platform findings

### 1. Ashby — easiest

Official public endpoint:
`GET https://api.ashbyhq.com/posting-api/job-board/{JOB_BOARD_NAME}?includeCompensation=true`

The public Job Postings API returns published jobs, descriptions in HTML/plain text, location, workplace type, employment type, publication date, job URL and apply URL. The board name is the path segment on the employer's Ashby-hosted board. No pagination is documented for this endpoint.

Important distinction: Ashby's other endpoints such as `jobPosting.list` and `job.list` require the `jobsRead` permission. Do not use them as the public-board adapter. The public endpoint has a different access model.

Implementation notes: validate listed/unlisted behavior, stable IDs, compensation optionality, secondary locations and the difference between jobUrl and applyUrl.

Primary source: https://developers.ashbyhq.com/docs/public-job-posting-api  
Authenticated API distinction: https://developers.ashbyhq.com/reference/jobpostinglist

### 2. Lever — easiest

Official public endpoint:
`GET https://api.lever.co/v0/postings/{SITE}?mode=json`

Lever documents public job-board postings and supports `skip` and `limit` pagination. The response includes job content and application/job links. EU-hosted boards use `api.eu.lever.co`; do not assume the global host. Lever also provides an individual-posting method.

Implementation notes: resolve site slug and region from the actual careers URL; test paging until the returned count is complete; preserve hosted job and apply URLs separately.

Primary source: https://github.com/lever/postings-api

### 3. Teamtailor — easy

Official RSS pattern: append `.rss` to the employer's Teamtailor jobs page, for example `https://career.teamtailor.com/jobs.rss`.

Teamtailor's support documentation says the public RSS feed includes title, description, publication date, advert URL, remote status, global ID, locations, department, role and division. The separate Teamtailor Public API requires an API key, so Scout should prefer RSS.

Implementation notes: parse RSS/XML, HTML-escaped descriptions and canonical advert links. Do not infer that every company with a custom careers domain is Teamtailor; verify the actual page and feed.

Primary source: https://support.teamtailor.com/en/articles/11171756-rss-feed-how-to-guide  
API authentication reference: https://docs.teamtailor.com/

### 4. Personio — easy, add to scope

Official XML feed pattern:
`https://{account}.jobs.personio.com/xml?language=en`  
Some accounts use `jobs.personio.de`.

Personio's help centre states that the employer must enable the XML interface in Recruiting settings. Once enabled, the feed is accessible without credentials. The feed can be used to populate an external careers site; candidates are redirected to the Personio job page to apply.

Implementation notes: a feed may be absent because the employer has not enabled it. Parse XML and language explicitly. Preserve the original source URL and the Personio job/application URL. Handle .com/.de hosts and redirects.

Primary source: https://support.personio.de/hc/en-us/articles/207576365-Integrate-jobs-from-Personio-into-your-website-via-XML  
FAQ: https://support.personio.de/hc/en-us/articles/29375445597725-Frequently-asked-questions-on-XML-job-integration

### 5. Recruitee — easy–moderate, use feeds

Recruitee provides public XML offer feeds, including:

- `https://{company}.recruitee.com/api/feeds/offers.xml`
- `https://{company}.recruitee.com/api/offers.xml`

The official support material describes the XML feeds and the feed documentation says only published offers appear. The Careers Site API is a separate route and now requires a company-generated token. The API reference says unauthenticated calls will return 401 from 10 February 2027. It also explicitly says the XML offer feed and jobs widget are not covered by that token requirement.

Implementation notes: choose the public XML feed rather than building around the token-protected Careers Site API. Recheck vendor documentation before release because access policy is changing. Validate actual board availability and application URLs.

Primary sources:

- https://support.recruitee.com/en/articles/8213076-faq-api
- https://docs.recruitee.com/docs/feed
- https://docs.recruitee.com/reference/authentication-1

### 6. Workable — easy–moderate, undocumented public widget

Observed public endpoint:
`GET https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true`

Independent live research reports that the widget returns employer name, job list, descriptions, locations and apply URLs without a key. This is distinct from Workable's documented customer API at `/spi/v3/jobs`, which requires an employer-generated API token and `r_jobs` scope.

Implementation notes: the widget endpoint is not the same as the authenticated customer API and should be labelled observed/undocumented. Verify against actual employer boards, test throttling and redirects, and avoid aggressive probing.

Sources:

- https://hwangbyeongseon.github.io/ats-job-feed-recipes/workable-api.html
- https://help.workable.com/hc/en-us/articles/115012771647-Using-the-Workable-API

### 7. Greenhouse — existing reference

Official endpoint:
`GET https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true`

Greenhouse documents public GET access without authentication. The application-submission POST is a separate authenticated operation. The project user confirms the Greenhouse extraction-to-Thungatha flow has been exercised end to end. Keep Greenhouse as the reference adapter and retain its fixture, complete-board and reliability evidence.

Primary source: https://docs.greenhouse.io/job-board

### 8. SmartRecruiters — moderate

Official Posting API documentation classifies the Posting API as public and the authentication guide lists it among APIs that do not require authentication. Do not confuse this with API-key/OAuth access for other SmartRecruiters API capabilities or with internal postings. The public Posting API is intended to expose postings that have been made public. The list API is paginated; detailed posting data may require a second request.

Implementation notes: verify the exact public list and detail endpoints from the current API reference and test them without credentials. Keep internal postings out of scope. Confirm that returned URLs land on the correct public vacancy/application flow.

Primary sources:

- https://developers.smartrecruiters.com/docs/posting-api
- https://developers.smartrecruiters.com/docs/authentication

### 9. BambooHR — moderate, undocumented

Observed careers endpoints:

- `GET https://{subdomain}.bamboohr.com/careers/list`
- `GET https://{subdomain}.bamboohr.com/careers/{job_id}/detail`

Independent endpoint investigations report that the list response is lightweight and does not contain full descriptions; detail calls are required per vacancy. These are not established as a supported public API contract by BambooHR's official developer documentation.

Implementation notes: do not mistake BambooHR's customer HR API for its public careers page. Validate the two careers endpoints against actual employer boards, confirm the detail response and apply link, and record fields that are missing (including posting date/remote data where absent).

Research reference: https://github.com/HwangByeongSeon/ats-job-feed-recipes

### 10. Breezy HR — moderate–hard

Observed public listing:
`GET https://{company}.breezy.hr/json`

The JSON feed returns published vacancy summaries but omits full descriptions. Breezy's documented API is rooted at `https://api.breezy.hr/v3` and requires an account token; it reads the authorised company's account and is not a cross-employer public API.

Detail extraction is not settled. One live investigation reports that the public feed has no descriptions and that missing job IDs redirect to the portal homepage. Another independent investigation reports schema.org JobPosting JSON-LD on job detail pages. This conflict must be resolved against actual employer portals before implementation. Never assume the detail route or treat a summary-only feed as a complete vacancy extraction.

Sources:

- https://developer.breezy.hr/reference/overview
- https://adderleydata.com/guides/breezy-hr-job-board-api/
- https://github.com/jloor/ats-fetch/blob/main/docs/ats-survey.md

### 11. Zoho Recruit — hard

The public careers page pattern is:
`https://{tenant}.zohorecruit.com/jobs/Careers`

No documented unauthenticated public jobs API was established in this research. Independent investigation describes job data embedded as escaped JSON in the careers HTML. This is an implementation observation, not a vendor-supported contract.

Implementation notes: inspect the actual page and script/data structure, parse defensively, and validate detail/application links. Zoho's documented career-site features do not establish a general public cross-employer API.

Primary product reference: https://www.zoho.com/recruit/career-site.html  
Observed endpoint research: https://hiringindex.org/sources/zoho

### 12. Workday — hard

Observed public careers-site endpoint:
`POST https://{tenant}.{cluster}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs`

Typical request body:
`{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`

Workday does not publish this as a general public job-board API. The endpoint is the JSON service used by public career pages. It commonly returns 20 jobs per page; descriptions/details require another GET using the posting's `externalPath`. Host cluster, tenant and site are separate values and must be extracted from the actual employer URL. Large boards can hit result caps or unusual pagination behavior.

Implementation notes: keep the host/tenant/site parser isolated; test real employer boards; use conservative concurrency; validate completeness from totals; never mark jobs removed after partial or capped extraction.

Research references:

- https://adderleydata.com/guides/workday-job-board-api/
- https://ctriolab.com/jobs/workday-jobs-api/

### 13. SAP SuccessFactors — hard, legacy route is retiring

SAP SuccessFactors Career Site Builder is a configurable product integrated with SuccessFactors Recruiting. The official SAP documentation describes implementation/configuration steps requiring administrative/implementation access. This means there is no single verified unauthenticated endpoint that can safely be assumed for every employer.

Important lifecycle issue: SAP's legacy RSS response for XML endpoints on career sites reached end of development on 14 November 2025 and is scheduled for deletion on 14 May 2027. Do not invest in a new adapter whose only strategy is this retiring response.

Implementation notes: treat each employer career site as a tenant-specific investigation. Identify whether the employer uses Career Site Builder, a custom domain, an iframe, a public widget or another supported page route. Validate public access and application destinations before implementation.

Sources:

- https://help.sap.com/docs/SAP_SUCCESSFACTORS_RECRUITING/8477193265ea4172a1dda118505ca631/04a49707944946338c35e6c86aab94e5.html
- https://learning.sap.com/courses/sap-successfactors-recruiting-candidate-experience/describing-the-new-features-and-enhancements-in-the-2h-2023-release_f278480f-f3fe-4bf0-9c57-ad63fdda3f5b

### 14. Simplify.hr — hard, locally important

Simplify.hr is a South African-built recruitment platform. Its own site describes Simplify Hire as an ATS and names South African customers. Live official employer career pages were verified for Media24 and homechoice. The homechoice board currently exposes Cape Town vacancies. These are valuable local sources.

However, this research did not establish a documented, unauthenticated public job API or RSS feed. Do not assume the URL pattern `{company}.simplify.hr` implies a JSON API. Inspect the public careers page, network requests and application links. The vendor's customer-facing API or integration access may require credentials.

Sources:

- https://simplify.hr/
- https://simplify.hr/hire
- https://media24.simplify.hr/
- https://homechoice.simplify.hr/
- https://jobs.simplify.hr/?company=homechoice

### 15. Neptune / eRecruit — hard, do not conflate products

Shoprite's live careers portal is hosted at `shoprite.erecruit.co` and exposes vacancies, including Cape Town roles. Separately, Graylink markets Neptune as its ATS and lists enterprise customers in sectors including retail, mining, energy and financial services. The evidence reviewed does not establish that Shoprite's eRecruit portal is the Graylink Neptune product, nor that Clicks or MultiChoice use Neptune.

No general public eRecruit/Neptune API or stable feed was established. Treat each portal as a separate employer-specific source until its vendor/product identity and public data interface are confirmed.

Sources:

- https://shoprite.erecruit.co/candidateapp/jobs/browse
- https://www.itweb.co.za/office/graylink/about

### 16. Placement Partner — hard, but retain

Placement Partner is a recruitment-agency source pattern, not a direct-employer ATS. Keep it in scope because agency vacancies can still lead candidates directly to a valid vacancy and application journey.

The URL pattern supplied for investigation is:
`https://placementpartner.co.za/live/agency.php?agency={agency_id}`

This research did not establish a documented public API, a reliable global agency directory, or a complete stable agency-ID mapping. Implement as a separate agency-source adapter only after live agency pages are sampled.

Candidate-link policy:

- Accept a direct link to the exact vacancy and its application process.
- Accept a redirect that canonicalises or moves to the same exact vacancy/application page.
- Flag redirects to a generic agency homepage, search results, a different vacancy, login wall or broken page.
- Persist original URL, redirect chain, final URL, status code and validation outcome.
- Do not reject a valid job merely because its application page is hosted by the agency rather than the employer.
- Do not count recruitment agencies toward direct-employer coverage.

### 17. JobAdder — partner/customer-dependent

JobAdder documents an API, but partner guidance says OAuth2 experience is required and advises developers to contact its API team. Its OAuth flow grants access to a JobAdder user's account. This is not a general unauthenticated endpoint that Scout can call for any agency.

Implementation notes: keep JobAdder as a possible integration where an agency/customer authorises access. Public agency job widgets or pages can be investigated separately, but do not assume API access from a public job listing URL.

Sources:

- https://jobadder-partners.zendesk.com/hc/en-us/articles/8359239946127-JobAdder-API
- https://jobadderapi.zendesk.com/hc/en-us/articles/360022196774-OAuth2-Authentication

### 18. Leaply — not yet established as an ATS adapter

The evidence reviewed describes Leaply as a recruitment engine/marketplace that finds, screens and verifies candidates and delivers candidates to employers. It does not establish a conventional public employer vacancy board or a public vacancy feed. The supplied `{company}.leap.ly` employer-board pattern and named employer mappings were not verified.

Keep Leaply in the employer/source discovery backlog, but do not count it as a supported ATS adapter until a candidate-facing job listing URL, public retrieval method and direct application path are demonstrated.

Source: https://www.linkedin.com/company/leaply/

## Employer/source verification findings

These are examples verified from official employer or platform pages during this research. They are not a complete customer list, and they do not prove every company named in the initial lead list uses the claimed platform.

| Platform        | Verified local employer/source evidence                                                          | Confidence     |
| --------------- | ------------------------------------------------------------------------------------------------ | -------------- |
| Greenhouse      | Takealot Group and Ozow official hosted boards                                                   | Verified board |
| Simplify.hr     | Media24 and homechoice official hosted career pages; homechoice listing includes Cape Town roles | Verified board |
| Teamtailor      | Biovac official Teamtailor career page with multiple Cape Town roles                             | Verified board |
| eRecruit        | Shoprite official hosted portal with Cape Town vacancies                                         | Verified board |
| Breezy HR       | ShopriteX official Breezy HR portal with Cape Town technology roles                              | Verified board |
| SmartRecruiters | WNS official SmartRecruiters careers page lists Cape Town jobs                                   | Verified board |

The Shoprite/ShopriteX result is particularly important: one corporate group may expose different business units or recruitment streams through different systems. Scout's employer model must support multiple independent sources per employer. Never force one company to one ATS.

The following names from the initial lead list remain unverified in this research as exact employer-to-platform mappings: Old Mutual/Absa/Pick n Pay/Sanlam/Standard Bank to Workday; TFG/Mr Price to Simplify.hr; Capitec/Standard Bank/Allan Gray/Absa/Bowmans to Leaply; Telkom/Capitec/Discovery/SARS to SuccessFactors; Woolworths Financial Services/Concentrix to SmartRecruiters; Luno/Aerobotics/SweepSouth to Lever; Yuppiechef/Lulalend/NML to BambooHR; Totalstay/Blackbeard Technology to Breezy HR; Skynamo/DataProphet to Recruitee; and the listed agencies to Placement Partner. Do not discard these companies. Keep them as source-discovery leads and verify each through the employer's own careers site.

## Redirect and application-link validation standard

Redirects are not inherently a failure. The candidate must be able to reach the same vacancy and apply.

For every extracted vacancy, store:

- `source_listing_url`: the page/feed record from which Scout discovered it.
- `job_url_original`: exact URL supplied by the ATS/feed.
- `job_url_final`: final URL after a bounded redirect check.
- `redirect_chain`: ordered URLs and HTTP status codes.
- `apply_url`: explicit application URL where supplied.
- `link_validation_status`: `valid_exact_job`, `valid_same_job_redirect`, `generic_redirect`, `wrong_job`, `login_required`, `broken`, `blocked`, or `not_checked`.
- `last_link_checked_at`.

Never follow unlimited redirects, submit forms, or bypass access controls. Use bounded HEAD/GET checks, with GET fallback where HEAD is unsupported. Do not treat a redirect to an agency-hosted application form as invalid if the vacancy identity remains exact. If link validation fails, retain the vacancy as an exception rather than silently dropping the employer/source.

## Implementation sequence for M4

### First wave — momentum and broad coverage

1. Ashby
2. Lever
3. Teamtailor RSS
4. Personio XML
5. Recruitee XML
6. Workable public widget
7. Greenhouse reliability/evidence closure

### Second wave — public but more involved

8. SmartRecruiters
9. BambooHR
10. Breezy HR

### Third wave — complex/local strategic sources

11. Simplify.hr
12. eRecruit / Neptune investigation
13. Workday
14. Zoho Recruit
15. SAP SuccessFactors

### Separate source pipelines

16. Placement Partner — agency source pipeline
17. JobAdder — customer/partner-authorised integration only
18. Leaply — discovery lead pending proof of a public job feed

The order inside the hard group should be adjusted if verified employer-source evidence shows a high-value Cape Town employer depends on one platform. Complexity should affect sequencing, not whether the company is retained.

## Acceptance gates for every adapter

1. Official employer careers URL and employer identity are recorded.
2. ATS/platform relationship is evidenced by the employer's official site.
3. Public retrieval method and authentication requirements are tested.
4. A representative live source returns meaningful vacancies, not merely HTTP 200.
5. Published-job completeness and pagination/total behavior are understood.
6. Description and location completeness are measured; missing fields are explicit.
7. Stable source IDs and original job/application URLs are retained.
8. Redirect behavior reaches the exact vacancy/application flow.
9. Fixtures and contract tests cover success, empty, malformed, blocked, rate-limited, partial and transient outcomes.
10. Failed/partial runs cannot expire jobs.
11. Existing employer/source records can be refreshed idempotently without duplicate companies or vacancies.
12. Only then may registry status move from candidate to implemented/verified. Production readiness remains a separate acceptance decision.

## Research limitations

This is a technical platform assessment, not proof of a complete South African ATS customer census. Vendors generally do not publish a global customer directory. Several findings rely on observed public endpoints documented by independent engineering investigations rather than vendor-supported contracts. Such routes must be live-tested and rechecked before production. Company examples supplied as leads have deliberately not been promoted to verified mappings without official evidence.
