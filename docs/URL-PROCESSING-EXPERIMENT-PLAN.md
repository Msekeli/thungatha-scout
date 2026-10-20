# URL Processing Experiments

## Purpose

This phase is for investigation, not production implementation. We will manually provide company careers-page URLs, test them one at a time, observe how each website behaves, and use the results to decide how URL processing should work.

We are not implementing automatic company discovery or scheduled job monitoring in this phase.

## Working approach

1. Keep the existing company register in `backend/data/companies.csv` as the seed list. Do not overwrite it with experiment output.
2. Select one company from the register and manually add its verified careers-page URL.
3. Run a small Python experiment against that URL.
4. Record the response and inspect what content Python received.
5. Determine whether the page appears to be a normal HTML page, an ATS-hosted page, a JavaScript-rendered page, a redirect, blocked, or otherwise inaccessible.
6. Check whether job titles, locations, descriptions, and application links are present in the returned content. Do not assume they can be extracted just because the page loads.
7. Save observations in a separate experiment log.
8. Repeat with varied companies and ATS platforms before choosing an implementation approach.

## Suggested initial test matrix

| Test | What to observe | Why it matters |
| --- | --- | --- |
| URL access | HTTP status, final URL after redirects, content type, response time, errors | Establish whether Python can reach the page |
| HTML response | Whether useful HTML is returned and whether it contains visible job information | Establish what a basic HTTP request can inspect |
| JavaScript dependency | Whether the returned HTML appears to be only a shell or requires client-side rendering | Identify pages that may need a browser-based experiment |
| ATS/platform | Any visible platform clues, URL patterns, page metadata, or branding | Group similar page types based on evidence |
| Job content | Presence of title, location, description, and application URL | Measure extraction feasibility |
| Repeatability | Whether the same URL gives a similar result on a later manual test | Avoid designing around a one-off response |
| Failure behavior | Timeout, rate limit, access denied, bot check, broken link, unexpected content | Record limitations without treating every failure as a coding defect |

## How to run the investigation

Start in the terminal. Terminal output is sufficient for the first experiments because it exposes the HTTP status, redirects, headers, response size, and snippets of returned HTML without requiring a UI. A frontend would add another layer before we know which observations and controls are useful.

For each test, record:

- Date and time of the test
- Company name and submitted careers URL
- Final URL after redirects
- HTTP status or exception
- Response content type and approximate size
- Whether the content appears to contain job listings
- Suspected ATS/platform, with evidence and confidence
- Whether useful job fields were found
- Whether a browser/JavaScript experiment may be needed
- Notes and next experiment

Do not store cookies, authentication tokens, or other secrets in the log. Do not repeatedly hammer a website; use small, deliberate requests and respect site access rules.

## Experiment log template

Copy this section for each manually tested company.

### Company: [name]

- Test date:
- Submitted careers URL:
- Final URL:
- HTTP status / error:
- Content type:
- Response size:
- Redirected:
- Suspected page type / ATS:
- Evidence for page type:
- Job titles present in response:
- Locations present in response:
- Descriptions present in response:
- Application links present in response:
- JavaScript/browser experiment likely needed:
- Outcome: not tested / accessible / partially inspectable / extraction promising / blocked / failed
- Notes:
- Next question to investigate:

## Decision gate

After a representative sample has been tested, compare the evidence before choosing tools:

- If ordinary HTTP requests return useful content for most tested pages, continue investigating a lightweight HTTP + HTML parsing approach.
- If some pages return useful content but others appear JavaScript-rendered, test browser automation only on those examples.
- If an ATS exposes structured public job data or a stable public endpoint, investigate it separately and verify that it is appropriate to use.
- If a site blocks requests or requires access we do not have, record the limitation and do not attempt to bypass access controls.

These are hypotheses to test, not decisions already made.

## Later phase — not part of the current work

Only after URL processing has been evaluated should we design a manual company-entry experience, a review screen, and eventually scheduled checks for new or changed jobs. Monitoring should compare current results with previously recorded jobs and should not be enabled by default during this investigation.
