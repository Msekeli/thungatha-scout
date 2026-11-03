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

## Registry responsibilities and data boundaries (3 November 2026)

The initial registry is split into two files because adapter definitions and employer/source mappings are independently maintained concepts:

- `backend/registry/ats-adapter-registry.json` describes reusable adapter definitions: adapter key, implementation status, retrieval method, known capabilities, required configuration fields and adapter-level constraints.
- `backend/registry/employer-source-registry.json` describes organizations and their recruitment sources: employer identity, organization classification, official careers entry point, source-to-employer relationship, adapter-specific configuration and evidence supporting each verification claim.

The adapter registry must not contain employer-specific board identifiers or employer verification evidence. The employer/source registry must not become a copy of generic adapter capabilities. Adapter code should consume employer-specific configuration from the registry rather than hardcoding board slugs, tenants or site identifiers.

### Verification boundaries

Keep these claims independent:
1. Employer identity and organization classification.
2. Employer's Cape Town presence.
3. Relationship between the employer's official website/careers page and the external source or ATS board.
4. Technical retrieval method and adapter capabilities.
5. Source terms, permission and operational constraints.
6. Human approval to use/publish the source or resulting records.

Evidence supporting one claim does not automatically verify another. In particular, a verified ATS board mapping does not establish Cape Town presence, source permission, adapter implementation readiness or approval.

Unknown capabilities and unverified claims must remain explicitly unknown or pending. Do not infer a capability because an endpoint appears plausible or because one request succeeded. The current registry entries are an initial working dataset; their presence does not mean M1 persistence, schema validation, source approval or production readiness is complete.

### File naming and responsibility

Every file has one clearly defined primary responsibility. Names should state that responsibility clearly and specifically without becoming unnecessarily long. Split independently maintained concepts; do not split a cohesive concept into many files merely to avoid a longer name.


## Decision record — v1 implementation baseline (3 November 2026)

V1 is limited to Greenhouse and Workday. Recruiter self-service and other ATS platforms remain out of scope. The private Next.js admin interface is required in v1; it is not a public job-search frontend.

### Product workflow
- The employer is the primary management entity. An employer can have multiple independent recruitment sources; vacancies retain employer and source provenance.
- Add Company is URL-first. The administrator pastes a careers/ATS URL; the backend detects the ATS, inspects the source and extracts employer metadata where reliable. The administrator confirms the employer identity and source relationship before registration.
- Manual ATS selection is a fallback and override. V1 supports Greenhouse and Workday only.
- Adding an employer to an existing adapter is configuration-driven and must not require employer-specific adapter code. A new ATS may require one new adapter implementation.
- Adding a source to an existing employer must not create a duplicate employer. Archiving a source must not remove its employer or other sources.
- Employer/source approval and vacancy approval are separate. Only approved, validated vacancy versions may publish.

### Technical ownership
- Frontend: Next.js App Router, TypeScript and Tailwind CSS.
- Backend: one Python Azure Functions Function App using Python v2. HTTP functions expose admin operations; timer functions perform bounded scheduled work. Triggers delegate to shared application services.
- Operational persistence: PostgreSQL. Python owns business rules and authoritative writes. Next.js calls the backend API and does not write directly to PostgreSQL.
- Publishing: approved records go idempotently to the existing Thungatha Supabase integration. Scout operational state remains separate.
- No microservices, separate Function Apps per ATS or second frontend ORM without demonstrated need.

### Adapter behavior
- Greenhouse uses its documented public Job Board GET API for a known board token. It is board-specific, not a global customer directory.
- Workday uses observed public careers-site CXS JSON endpoints. This is undocumented behavior, not a guaranteed public API. Parse host, tenant and site separately and validate each board.
- For https://myhcm.wd3.myworkdayjobs.com/digioutsource, expected values are host myhcm.wd3.myworkdayjobs.com, tenant myhcm and site digioutsource. Do not confuse tenant and site.
- One Workday adapter may contain explicitly tested compatibility strategies. Never create one adapter per employer or speculative strategies without evidence.
- A source test must validate meaningful vacancy data, not merely HTTP 200. Distinguish empty, not-found, blocked, rate-limited, malformed, partial and transient outcomes.
- Adapter definitions remain separate from employer-specific source configuration. Never hardcode board tokens, tenants or site identifiers in adapter code.

### Employer identity and logos
- Prefer authoritative ATS board metadata, then official careers-page metadata/structured data and validated public board response metadata. A Workday job payload may provide evidence but is not guaranteed to exist or contain the employer name.
- Never infer a company name solely from a URL slug. Ask for administrator confirmation/input when extraction is uncertain.
- Logo retrieval is best-effort: verified ATS image, official employer website, separately evaluated provider, then admin upload/replacement. Do not depend on the retired Clearbit Logo API. Store logo source/attribution; missing logos never block registration.

### Persistence and lifecycle
- Core records: employers, employer_sources, vacancies, vacancy_versions, extraction_runs and review/audit records.
- Enforce source-scoped external identity with a unique constraint on (source_id, external_job_id). Use normalised SHA-256 fingerprints to detect meaningful content changes.
- Keep vacancy lifecycle separate from review/publication state. Preserve the latest extracted version separately from the approved/published version. Changed content creates a version and may require review; it must not silently overwrite an approved version.
- Extraction runs record start/end, outcome (success/partial/failed), duration, jobs found/added/updated/expired, pagination/completeness and sanitised diagnostics.
- Source operational status (pending_verification, active, paused, archived) is separate from computed health (unknown, healthy, warning, failed).
- Failed or incomplete runs must not expire vacancies. Expiry requires a sufficiently complete successful inventory comparison.
- Archive employers and sources rather than physically cascading deletion through vacancy and extraction history. Preserve audit records.

### Admin v1
Navigation: Dashboard, Companies, Vacancies and Review Queue. Source health, tests and extraction history are embedded in Company Details. Add Company is URL-first, detects the ATS, supports manual override, previews metadata and requires confirmation. Company name is not routinely typed; manual entry is a fallback. Company operations include edit, add source, test, pause/resume and archive.

### Initial acceptance target
Register a Greenhouse board and the DigiOutsource Workday board through the admin UI, confirm extracted employer metadata, test retrieval, view real vacancies and manage employer/source records. New employers using either supported adapter require configuration only, not backend code changes. This is a target, not a claim that the current repository already implements it or that live integrations have passed.


## Decision record — autonomous ingestion and isolated Scout persistence (3 November 2026)

This decision supersedes conflicting v1 implementation statements above and in older planning documents.

### Product operating model
- Scout is designed to operate unattended after an administrator registers and verifies an employer/source.
- The administrator's normal responsibility is to paste an official careers/ATS URL, inspect the source preview, confirm employer identity and official source relationship, and activate the source.
- Scheduled extraction, normalisation, deterministic quality validation, deduplication, lifecycle reconciliation and publication run automatically.
- Routine vacancy-by-vacancy human approval is removed. It is not a release prerequisite for every vacancy.
- Vacancies that pass the configured deterministic publication gates are automatically eligible for idempotent publication to Thungatha.
- Exceptions are placed in an exception-review queue. Examples include missing or malformed application URLs, insufficient job details, ambiguous employer/source attribution, uncertain Cape Town relevance, possible duplicates, suspicious or malformed content, and materially changed content that cannot safely be assessed automatically.
- Admins can reject or unpublish a record, correct permitted fields, pause a source, deactivate/archive an employer or source, and inspect the decision history.
- AI may assist with extraction or classification, but cannot override hard validation gates or invent evidence. Low-confidence AI output is an exception, not an automatic approval.
- Every automatic publish, rejection, suppression and exception decision must persist a reason, rule/version, evidence references and timestamps.

### Publication quality gates
A vacancy may auto-publish only when:
1. Its employer and source are active and verified to the required level.
2. The source is an employer-authorised official careers/ATS source and its use complies with applicable access restrictions and terms.
3. A stable source-scoped vacancy identity exists.
4. Required fields are present: meaningful title, employer identity, useful description, credible location or explicit remote arrangement, and a working/recognised application destination.
5. Location and initial Cape Town scope are supported by evidence; unknown location is not silently treated as Cape Town.
6. It is not a confirmed or unresolved high-confidence duplicate.
7. Freshness and lifecycle checks pass without treating a failed/partial extraction as evidence of removal.
8. The record passes content safety, URL and schema validation.
9. The publishing payload matches the Thungatha contract and the idempotency key is stable.

Records failing a hard gate are suppressed/rejected with a reason. Records with uncertainty that cannot be resolved deterministically go to exception review. A successful ATS retrieval is not, by itself, proof that a vacancy should be published.

### Persistence and hosting decision
- Scout operational persistence is a dedicated Supabase project using PostgreSQL, separate from Thungatha's existing Supabase project.
- Thungatha's existing Supabase project remains the destination for approved/qualified public-facing records only.
- Raw, incomplete, rejected, exception and extraction-history data remain in Scout and are never copied wholesale into Thungatha.
- Scout's database schema and credentials are isolated from Thungatha's. The backend owns all writes and business rules; the React browser client never receives a service-role key.
- Azure Table Storage and a Scout PostgreSQL database hosted in Azure are not v1 requirements. Do not provision Azure storage or databases unless a later cost/technical review explicitly changes this decision.
- Frontend: React + TypeScript + Vite, hosted on Vercel.
- Backend: Python HTTP API and scheduled/background processing, hosted on a provider selected for reliable low-cost hosting. Keep the backend portable. Azure Functions remains a candidate, not a mandatory dependency.
- The current Azure for Students credit is exhausted. Do not upgrade the subscription, create paid Azure resources or assume Azure free allowances will cover persistent storage/compute without a verified cost calculation and explicit user approval.
- Supabase Free may be used for development and a low-volume pilot only after checking current limits, inactivity pausing, backup and production reliability implications. Plan a paid tier or alternative before production depends on uninterrupted service.

### Data retention and storage discipline
- Keep the Scout database focused on structured operational records and the latest meaningful vacancy versions.
- Avoid storing full HTML/page snapshots by default. Retain raw evidence only where it materially supports audit/debugging and apply a bounded retention policy.
- Do not create a new vacancy version for unchanged content.
- Keep extraction run summaries and exception/audit evidence; define retention/archival rules before volume grows.
- Publishing to Thungatha is a one-way, validated, idempotent integration. Scout retains its own operational history.

### Superseded decisions
The following earlier statements are no longer current: Next.js admin frontend; Azure Table Storage as mandatory operational persistence; PostgreSQL operational storage hosted as part of the prior Azure-first plan; routine human approval of every vacancy; and a rule that only human-approved vacancy versions can publish. Historical entries remain as decision history but must not guide new implementation.
