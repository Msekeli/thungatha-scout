# Experiment 002 — BeingIT Careers

## Objective

Inspect one manually supplied careers URL and determine how the listing and vacancy detail pages can be retrieved. This is an exploratory experiment only; it does not implement discovery, scheduled monitoring, or production ingestion.

## Starting URL

- Careers page: https://www.beingit.co.za/Careers
- Vacancy detail inspected: https://www.beingit.co.za/Careers/Vacancy/DMLC001
- Vacancy: Digital Marketing & Lead Conversion Manager
- Reference: DMLC001

## Careers page observations

- HTTP GET succeeded with status 200.
- Final URL remained `https://www.beingit.co.za/Careers`.
- Content type: `text/html; charset=utf-8`.
- Response size observed: 38,859 bytes.
- Page title: `BeingIT® | Careers`.
- The page HTML included vacancy titles and links to individual vacancy pages.
- Observed vacancies included Digital Marketing & Lead Conversion Manager; Graduate .NET Developer; Intermediate .NET Developer; Intermediate to Senior .NET Developer; Junior .NET Developer; Junior to Intermediate .NET Developer; and Senior .NET Developer.
- Individual vacancy links used paths such as `/Careers/Vacancy/DMLC001`.
- The listing's “Apply Now” links pointed to `#`.

## Vacancy detail observations

- HTTP GET succeeded with status 200.
- Final URL remained `https://www.beingit.co.za/Careers/Vacancy/DMLC001`.
- Content type: `text/html; charset=utf-8`.
- Response size observed: 19,826 bytes.
- Page title: `BeingIT® | Careers | Vacancy | Digital Marketing & Lead Conversion Manager`.
- The page HTML included the job title, reference, application instructions, company information, requirements, benefits, and an “Apply Now” control.
- The page text contained an application modal labelled “Job Application Form” with Previous, Submit, and Next controls.
- Script references observed:
  - `/js/modernizr?v=4.2026.604.19327`
  - Google Tag Manager / Google Analytics script
  - `/js/layout?v=4.2026.604.19327`
  - `/js/careers-vacancy?v=4.2026.604.19327`
- A form element was not printed by the initial inspection script. The application modal was present as a `div#application-modal.modal.fade`.

## Preliminary assessment

The careers listing and vacancy details are accessible with ordinary HTTP requests, and vacancy information is present in the returned HTML. Browser automation does not appear necessary for extracting the visible listing and detail-page content based on the evidence gathered so far.

The application UI appears to be a custom, JavaScript-assisted modal on BeingIT's own site. This is only a preliminary assessment: the actual submission mechanism, form fields, and any API endpoint have not been established. Do not classify the ATS or assume an external application provider without further evidence.

## Limitations and next investigation

- Only one vacancy detail page was inspected.
- The completeness and stability of the careers listing have not been tested over time.
- The application form's JavaScript and network requests have not been inspected.
- No production scraper, scheduler, database ingestion, or automated URL discovery was created.

If continuing this experiment, inspect the careers-vacancy JavaScript and the modal's form behavior to establish whether submission is handled by the site's own backend or another service. Keep this separate from the job-listing extraction decision.
