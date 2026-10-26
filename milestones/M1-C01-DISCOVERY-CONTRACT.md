# M1-C01 — Discovery Candidate and Evidence Contract

**Status:** In progress  
**Scope:** Data contract only. This does not select a search provider or authorize scraping.

## Candidate identity

- Every candidate has a deterministic candidate_id.
- If independent evidence has verified an official employer domain, the domain can form the stable identity key.
- Until identity is verified, the key is based on the observed HTTP(S) URL with query/fragment tracking removed. This is an observation identity, not a claim that two observations represent the same employer.
- Names and ATS board tokens alone are never sufficient to merge candidates or verify employer identity.
- If later evidence links two candidates to the same employer, merging is an explicit, auditable reconciliation rather than a silent overwrite.

## Evidence

Each evidence record captures method, optional query, observed URL, timezone-aware observation time, optional reference URL, excerpt and notes. Persist timestamps in UTC. Evidence must support the claim being made; a search snippet alone is not enough to mark an employer verified.

Candidate records keep official website/careers URLs separate from the URL where the candidate was observed. Identity status and organization type remain explicitly unresolved until evidence supports a decision. Location evidence is separately recorded.

## Discovery run outcomes

| Outcome | Meaning |
|---|---|
| success_with_results | Search completed and returned one or more candidates |
| success_empty | Search completed successfully with no candidates |
| request_failed | A discovery request failed, for example timeout or rate limit |
| discovery_failed | The overall discovery operation could not complete reliably |

Failed outcomes require an error code or message. Successful outcomes cannot carry failure details. Start/finish times must be timezone-aware and ordered. The current result model requires an empty candidate list for failed outcomes; a future orchestration contract may explicitly represent partial results.

## Safety and scope

- Initial geography is Cape Town, but location eligibility must be backed by location evidence.
- Discovery is not filtered by industry, company size or job title.
- Technical accessibility does not imply permission to use a source.
- A failed query is never recorded as a successful empty query.
- Human review remains required for uncertain identity/source classification.

## Verification

Tests use unittest and cover successful empty results, non-empty results, request failure, total discovery failure, identity validation, timezone validation and stable identity keys. Execute from backend/ with:

    python -m unittest discover -s tests/unit -v

The test command has not yet been executed in this environment because a runnable local checkout is unavailable.
