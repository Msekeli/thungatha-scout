# Thungatha Scout — Source of Truth

**Status:** Proposed baseline for review  
**Updated:** 3 November 2026

## Purpose
Thungatha Scout discovers companies operating in Cape Town, verifies their official recruitment sources, collects and tracks vacancies, and publishes approved company/job data to Thungatha. A minimal private admin UI lets the administrator resolve uncertain records.

## Scope
In scope: company discovery across industries and sizes; careers-page/ATS verification; classification; multiple sources per company; vacancy extraction, normalization, deduplication and lifecycle tracking; human review; approved publication; operational monitoring.

Out of scope for the initial release: a public job-search frontend duplicating Thungatha, recruiter self-service, complex multi-user administration, and autonomous AI agents.

## Geography and discovery rules
- Initial location scope is **Cape Town only**; do not silently expand to all Western Cape or Stellenbosch.
- Do not filter discovery by industry, company size, or job title.
- Companies may be approved even when they currently have zero vacancies.
- Approval requires evidence of company identity, Cape Town presence, organization type, and an official recruitment page.
- A careers page may redirect to an ATS if the relationship to the company is evidenced.
- ATS board discovery alone does not prove employer identity.
- Employer discovery uses two complementary channels: broad careers-page discovery and a separately measured ATS-footprint discovery process. ATS discovery improves coverage but does not replace employer-first verification.
- Initial ATS investigation priorities are Greenhouse, Workday, Lever, Breezy HR and Ashby. This is not a claim that all adapters are implemented or approved.
- Measure unique employer candidates and verified direct employers separately from ATS board counts and vacancy counts; high job volume from one employer is not broad employer coverage.
- Do not assume an ATS vendor exposes a public global customer directory. Discover board identifiers from multiple public footprints and third-party lead sources, then independently verify the employer relationship through its official website.
- Report search failure separately from a successful search returning no results.

## Organization classification
Use `direct_employer`, `recruitment_agency`, `staffing_company`, `hybrid`, `other`, or `unresolved`. Keep agencies/staffing firms separate from the direct-employer dataset. Do not automatically reject hybrid organizations; record evidence and review ambiguous cases.

## Review states
Company: `discovered`, `pending_review`, `approved`, `rejected`, `needs_review`, `inactive`.  
Source: `discovered`, `pending_verification`, `verified`, `temporarily_unavailable`, `invalid`, `needs_review`, `inactive`.

Preserve evidence and decision reasons. Do not silently delete unresolved or rejected records.

## Vacancy rules
Retain, where available: stable ID, company/source IDs, source job ID, title, description, location, employment type, source and application URLs, first/last seen, last checked, content fingerprint, status and publication state.

Statuses: `active`, `possibly_expired`, `expired`, `removed`, `unavailable`, `needs_review`. A timeout, rate limit, or source outage must not immediately expire vacancies. Do not deduplicate on title alone. Preserve source evidence.

## Human review and publishing
Human approval is an explicit backend state, not just a UI button. Publish approved companies even if they have no jobs. Publish only approved/validated records to Thungatha’s Supabase project. Scout’s internal state stays separate. Publishing must be idempotent and send only new/changed records where possible.

## Scheduling
Initial proposal: company discovery weekly while coverage is growing; reduce to monthly/on-demand when yield becomes low; company/source verification weekly; vacancy extraction every 8 hours; publish after successful batches plus a recovery pass; daily reconciliation. Schedules must be configurable. Avoid overlapping runs and bound retries.

## AI principles
Gemini and Groq are replaceable provider options. Use AI selectively for ambiguous classification and difficult extraction/normalization. Use deterministic code for URLs, deduplication, status changes, scheduling, and database writes. Validate structured AI output; low-confidence results go to human review. AI alone cannot approve or publish records. Check current models, quotas, and free-tier terms before enabling.

## Cost and security
The project is being built with limited Azure student credits (approximately USD $68 at document creation). Prefer consumption-based execution where suitable, avoid unjustified always-on resources, limit browser automation and AI calls, and monitor usage. The admin UI must authenticate and the backend must authorize every privileged action. Never hardcode credentials or expose service-role/API keys in frontend code.

## Future scope
A recruiter portal may be considered later. Recruiter-submitted jobs require separate ownership, provenance, verification, and moderation rules; they are not in the initial release.

## Decision governance
When decisions change, record date, reason, and impact; update affected documents. Inspect the live repository/tests before implementation. Historical Greenhouse-only notes and reports are evidence of prior experiments, not proof of current behavior.


## Decision record — dual-channel employer discovery (3 November 2026)

The discovery strategy is clarified to address low unique-employer yield from ATS-only job extraction:

- Keep broad Cape Town employer discovery active across industries and company sizes.
- Add a separate ATS-footprint discovery channel to find candidate employer/board pairs for Greenhouse, Workday, Lever, Breezy HR and Ashby.
- Treat ATS identifiers and third-party directories as leads. The employer's official website must support the claimed relationship before the source is verified.
- Report unique employer coverage separately from boards found and vacancies extracted. Do not optimise for job count at the expense of employer diversity.

This is a discovery strategy clarification, not approval to bypass source restrictions, use paid datasets, or treat all listed ATS adapters as production-ready.