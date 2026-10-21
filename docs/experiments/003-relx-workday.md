# Experiment 003 — RELX Careers / Workday

## Objective

Determine how to reach the actual RELX job listings from a manually supplied careers URL, and then test whether the listings can be retrieved through ordinary HTTP or a structured endpoint. This experiment does not implement automatic discovery, scheduled monitoring, or production ingestion.

## URLs tested

- Corporate careers page: https://www.relx.com/careers
- Join us page: https://www.relx.com/careers/join-us
- Job platform destination discovered: https://relx.wd3.myworkdayjobs.com/relx

## Corporate careers page observations

- HTTP GET succeeded with status 200.
- Final URL remained `https://www.relx.com/careers`.
- Content type: `text/html; charset=utf-8`.
- Response size observed: 66,263 bytes.
- Page title: `Careers – RELX - Information-based analytics and decision tools`.
- The page linked to corporate careers information pages rather than listing individual vacancies in the extracted links.

## Join us page observations

- HTTP GET succeeded with status 200.
- Final URL remained `https://www.relx.com/careers/join-us`.
- Content type: `text/html; charset=utf-8`.
- Response size observed: 76,035 bytes.
- Page title: `Join us – RELX - Information-based analytics and decision tools`.
- The page contains a link labelled “Click here to explore all jobs at RELX” pointing to `https://relx.wd3.myworkdayjobs.com/relx`.
- Additional “Read more” links point to the same Workday tenant with job-family filters and a worker-subtype filter.

## Preliminary assessment

RELX uses a Workday-hosted jobs site for its global vacancy listings. The corporate careers pages can be retrieved through ordinary HTTP, but they are not the job feed itself. The Workday tenant is the correct next target for assessing listing retrieval.

## Pending test

Not yet established:
- Whether Workday's job listings are present in the HTTP response.
- Whether Workday exposes a structured public endpoint suitable for listing retrieval.
- Whether browser automation is needed for listing or detail extraction.

The next experiment should make a single ordinary HTTP request to the Workday jobs URL and inspect status, final URL, page title, and a small number of job-related links or visible job titles. Do not investigate application submission or unrelated corporate pages.
