# Experiment 001 — Ozow Careers / Greenhouse

## Purpose

Record observations from a manual investigation of Ozow's careers page. This is research documentation only; no production extraction, automatic discovery, or scheduled monitoring was implemented.

## Test details

- Company: Ozow
- Submitted careers URL: https://ozow.com/jobs
- Test method: Python `httpx` and BeautifulSoup, followed by a direct HTTP request to the endpoint referenced by the page's embedded JavaScript
- Careers page HTTP status: `200`
- Final URL: `https://ozow.com/jobs` (no redirect observed)
- Content type: `text/html; charset=utf-8`
- HTML response size: `119,167 bytes`
- Page title: `Ozow Careers | Come Aboard The Rocket Ship!`
- Jobs section: `#jobs-list`
- Initial HTML contained a department prompt but no rendered job listings or application links inside the jobs section.

## Evidence and findings

The embedded script in the jobs section contains this request:

```text
https://boards-api.greenhouse.io/v1/boards/ozow/jobs?content=true
```

The script parses the response as JSON, then builds department filters and job cards using each job's title, location, department, and `absolute_url`. It also reads the job's `content` field.

This is direct evidence that Ozow uses Greenhouse's public job-board API to populate the careers page. The HTML page itself is accessible through a basic HTTP request, but its vacancy cards are populated asynchronously.

## Direct endpoint test

- Endpoint tested: `https://boards-api.greenhouse.io/v1/boards/ozow/jobs?content=true`
- HTTP status: `200`
- Content type: `application/json`
- Jobs returned in this test: `11`
- Job objects included title, location, department, application URL, and a non-empty `content` field according to the test.
- The response did not provide a `board` value at the top level in the tested payload.

Examples observed in the returned results:

| Job title | Location | Department |
| --- | --- | --- |
| Agentic AI Engineer | Cape Town | Technology |
| Content Strategist | Cape Town | Marketing |
| Enterprise Solutions Lead | Cape Town | Commercial |
| Fraud Manager | Cape Town | Legal |
| Junior Integration and Enablement Associate | Cape Town | Technology |
| Junior Software Engineer (AI-Enabled) | Cape Town | Technology |
| Marketing Manager | Cape Town | Marketing |
| Senior Data Engineer | Cape Town | Technology |
| Senior Software Engineer (AI-Enabled) | Cape Town | Technology |
| Software Engineer | Cape Town/Johannesburg | Technology |

The output displayed the first 10 jobs, while the endpoint reported 11 total.

## Assessment

- Outcome: extraction promising
- Page type: HTML careers page with JavaScript-loaded vacancies
- ATS/platform: Greenhouse, confirmed by the embedded endpoint URL
- Basic HTTP access: successful in this test
- Direct structured-data access: successful in this test
- Browser automation likely needed for this company: not for the tested job-list retrieval path, because the public JSON endpoint returned structured jobs directly
- Description completeness: not yet assessed; the test only confirmed that the `content` field was non-empty
- Repeatability: not yet tested
- Long-term endpoint stability: not yet assessed

## Next investigation

1. Inspect a sample `content` value to determine whether the job description is complete and usable.
2. Repeat the test later to understand whether results are consistent.
3. Test a manually verified company careers URL using a different ATS or page structure before choosing a general approach.

## Notes

These are observations from one manual test, not a guarantee that the same jobs remain available or that every Greenhouse board behaves identically. No credentials, cookies, or authentication tokens were recorded.
