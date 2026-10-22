# Postman: Cape Town job-feed API

This is the first integration slice for Thungatha Scout. It supports Greenhouse and Workday only. Every endpoint returns jobs whose reported location contains **Cape Town**; Stellenbosch and remote-only records are excluded.

## 1. Start the API

From the repository's `backend` directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.jobs_api:app --reload
```

Health check: `GET http://127.0.0.1:8000/health`

FastAPI's interactive endpoint documentation is at `http://127.0.0.1:8000/docs`.

## 2. Test Greenhouse

In Postman, send:

```http
GET http://127.0.0.1:8000/api/jobs/greenhouse?board=ozow&company_name=Ozow&max_jobs=25
```

The `board` value is a Greenhouse board token, not a URL. Ozow is the known investigation example. The company name is optional display metadata and should only be supplied when verified.

## 3. Test Workday

Use a confirmed public Workday board URL, for example the Betway Africa board used in the existing adapter tests:

```http
GET http://127.0.0.1:8000/api/jobs/workday?careers_url=https%3A%2F%2Fmyhcm.wd3.myworkdayjobs.com%2FBetway_Africa&company_name=Betway&max_jobs=10&include_details=false
```

Set `include_details=true` when you want the adapter to fetch full job descriptions. This makes additional requests and may take longer.

## 4. Response contract

Both endpoints return the same top-level shape:

```json
{
  "source_type": "greenhouse",
  "location_scope": "Cape Town, South Africa",
  "fetched_count": 11,
  "returned_count": 1,
  "jobs": [
    {
      "source_type": "greenhouse",
      "company_name": "Ozow",
      "company_key": "ozow",
      "source_id": "123",
      "title": "Example role",
      "location": "Cape Town, South Africa",
      "additional_locations": [],
      "department": "Engineering",
      "employment_type": null,
      "posted_at": null,
      "closing_at": null,
      "description_html": "<p>Job description</p>",
      "job_url": "https://...",
      "application_url": "https://...",
      "status": "active",
      "board_url": "https://..."
    }
  ]
}
```

The example values illustrate the schema, not live API output. Dates remain `null` if the source adapter does not provide a reliable date. Greenhouse's job URL and application URL are currently the same source-provided URL. Workday keeps the canonical listing URL separate from its application destination when the source provides distinct URLs.

## 5. What counts as passing

- The endpoint responds with valid JSON and a consistent schema.
- Every returned job has a title, location, and usable source/application URL.
- Returned job locations explicitly mention Cape Town; Stellenbosch and remote-only jobs are absent.
- `fetched_count` can be higher than `returned_count`, because the API filters the source results by location.
- A blocked or malformed source returns an error; it must not be reported as a successful feed with zero jobs.

This is a testing API, not yet a scheduled ingestion service or persistent job database. The source adapters and contract can be extended later without adding other ATS platforms now.
