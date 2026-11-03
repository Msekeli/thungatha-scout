# Local careers-page scanner

This experiment reads `cape_town_tech_companies.json`, visits each saved URL with Chromium through Playwright, follows likely job links, and saves the results to `career_page_scan_results.json`. It does not require a database or AI.

## Install

From the `backend/` directory, with the project virtual environment activated:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## First test: Sanlam

Run one company with a visible browser:

```bash
python scan_careers.py --company Sanlam --headed
```

Check the terminal summary and open `career_page_scan_results.json`. The report includes the status, count, detected job links, extracted page text, and errors.

## Scan the first three companies

```bash
python scan_careers.py --limit 3
```

## Scan all companies

After checking the first test:

```bash
python scan_careers.py
```

Optional arguments:

- `--company "Company Name"` scans one company.
- `--limit 5` scans only the first five companies.
- `--headed` shows the browser.
- `--max-jobs 100` caps detail pages per company.
- `--max-pages 5` caps listing/pagination pages per company.
- `--input path/to/file.json` changes the input file.
- `--output path/to/results.json` changes the report location.

## Interpret the status

- `jobs_found`: one or more likely job links were opened.
- `page_says_no_jobs`: the page explicitly says there are no vacancies.
- `no_jobs_detected`: the page loaded, but the scanner did not identify likely job links. This does **not** prove the company has zero jobs.
- `failed`: the page could not be scanned successfully.

The first version uses generic link and page-text heuristics. It will not correctly handle every website, custom JavaScript interaction, or every pagination pattern yet. Review results before treating counts or descriptions as complete. Scan results are local and are ignored by Git.
