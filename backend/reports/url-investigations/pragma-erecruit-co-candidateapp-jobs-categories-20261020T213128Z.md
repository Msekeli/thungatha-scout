# Careers URL Investigation

- Supplied URL: https://pragma.erecruit.co/candidateapp/jobs/categories/
- Final URL: https://pragma.erecruit.co/candidateapp/jobs/categories/
- HTTP status: 200
- Page title: Browse by Category  >  All Categories
- ATS detected: none detected
- Extraction success: True
- Jobs extracted in this response: 3

## Assessment

Structured ATS data or readable same-host vacancy pages were extracted; completeness still requires validation.

## ATS evidence

- No ATS evidence recorded.

## Adapter results

- **same_host_html_vacancies**: success=True; HTTP=n/a; reported jobs=n/a; candidate links=3; error=

## Extracted jobs

- **Browse by Category** — location not provided
  - https://pragma.erecruit.co/candidateapp/jobs/browse/
  - Description present: True
- **Search** — location not provided
  - https://pragma.erecruit.co/candidateapp/Jobs/Search
  - Description present: True
- **Sign up for an account** — location not provided
  - https://pragma.erecruit.co/candidateapp/SignUp
  - Description present: True

## Limitations

- One run does not guarantee completeness or long-term endpoint stability.
- Workday currently requests only the first page.
- Generic extraction checks at most 25 observed same-host detail links.
- No application forms are submitted and no account-protected content is accessed.
