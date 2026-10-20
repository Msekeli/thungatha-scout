# Thungatha Scout Backend

Python prototype for company discovery and careers-source verification.

## Current status

- [x] Candidate model stores source evidence.
- [x] Reusable HTTP/HTML inspection for a known URL.
- [x] CSV export for manual review.
- [ ] Select and implement a free-first discovery provider.
- [ ] Add supplied employer URLs as a benchmark dataset.
- [ ] Test JavaScript-rendered sites and add Playwright only if needed.

The discovery function intentionally returns no candidates until a provider is selected. Inspecting known URLs is not the same as discovering unknown employers.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m app.main
```
