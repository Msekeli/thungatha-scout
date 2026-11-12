# Zyte Cloud Crawlee smoke test

This temporary deployment package verifies that the existing Zyte Scrapy Cloud
project can install and execute Crawlee. It is not the Scout production worker.

The script runs one HTTP request to https://example.com/, with robots.txt
respect enabled, no retries, and no browser automation. It does not connect to
Supabase, call Zyte API, invoke AI providers, or write vacancy data.

## Deploy

From this directory, install the deployment client and authenticate with the
Scrapy Cloud API key (not the separate Zyte API key):

```bash
python3 -m pip install --user shub
shub login
shub deploy 885015
```

Do not paste the API key into chat, source files, or shell command history.

## Run

Open the Thungatha Scout project in Zyte Scrapy Cloud, choose Run, and select
`py:scout_zyte_smoke_test.py`. Use one unit and run it manually once.

A successful job must log the Python version, Crawlee version, HTTP 200,
non-empty response bytes, elapsed time, and `RESULT: SUCCESS`.

## Entitlement interpretation

A successful short job proves deployment and Crawlee execution only. It does
not prove the student entitlement. Compare the account's actual job limit and
data retention with the GitHub Student Developer Pack offer, which specifies
unlimited crawl time and 120-day retention. Stop if the dashboard indicates a
paid upgrade, additional unit, or charge.
