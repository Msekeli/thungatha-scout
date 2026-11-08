# Thungatha Scout — Source of Truth

**Status:** Proposed baseline for review  
**Updated:** 8 November 2026

## Purpose

Thungatha Scout discovers companies operating in Cape Town, verifies their official recruitment sources, collects and tracks vacancies, and publishes approved company/job data to Thungatha. A minimal private admin UI lets the administrator resolve uncertain records.

## Scope

In scope: company discovery across industries and sizes; careers-page/ATS verification; classification; multiple sources per company; vacancy extraction, normalization, deduplication and lifecycle tracking; human review; approved publication; operational monitoring.

Out of scope for the initial release: a public job-search frontend duplicating Thungatha, recruiter self-service, complex multi-user administration, and autonomous AI agents.

## Geography and discovery rules

- The product's initial vacancy relevance scope is **Cape Town only**; do not silently expand to all Western Cape or Stellenbosch.
- Do not use an employer's headquarters, registered address, city, province or country to determine whether its vacancies are relevant. Employer location is not a Companies-directory field or approval requirement.
- Register employers across industries and sizes when there is a credible basis to expect them to recruit for Cape Town roles, including historical Cape Town vacancy activity. Do not require a currently open Cape Town vacancy at registration time.
- Do not filter employer discovery by industry, company size, or job title.
- Company registration and source management are broad; vacancy-location relevance is evaluated per vacancy. Scout admin provides three vacancy location views: Cape Town, Western Cape and South Africa. Backend matching recognizes common location abbreviations and verified Cape Town suburbs; abbreviations are not shown in the UI. These admin filters do not independently change publication eligibility, which remains restricted to the separately configured publication geography.
- Approval requires evidence of employer identity, organization type, and an official recruitment page/source relationship. Cape Town headquarters or physical presence is not required.
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

Company discovery: weekly while coverage is growing; reduce to monthly/on-demand when yield becomes low. Company/source verification: weekly. Vacancy extraction: twice daily at 06:00 and 18:00 in the `Africa/Johannesburg` timezone. Each run starts at its scheduled time and may finish earlier when its work is complete; it must not be kept running merely to fill the time window. One hour is the maximum execution duration, not a target. A run that completes in 15 or 30 minutes exits normally. Enforce a hard one-hour timeout, prevent overlapping runs, and use bounded retries. Publish qualifying records after successful batches and run recovery for failed publication attempts. Reconcile lifecycle only from sufficiently complete successful extraction results; a failed/partial run must not expire vacancies. Schedules and execution limits must remain configurable.

## AI principles

Gemini and Groq are replaceable provider options. Use AI selectively for ambiguous classification and difficult extraction/normalization. Use deterministic code for URLs, deduplication, status changes, scheduling, and database writes. Validate structured AI output; low-confidence results go to human review. AI alone cannot approve or publish records. Check current models, quotas, and free-tier terms before enabling.

## Cost and security

The project is being built with limited Azure student credits (approximately USD $68 at document creation). Prefer consumption-based execution where suitable, avoid unjustified always-on resources, limit browser automation and AI calls, and monitor usage. The admin UI must authenticate and the backend must authorize every privileged action. Never hardcode credentials or expose service-role/API keys in frontend code.

## Future scope

A recruiter portal may be considered later. Recruiter-submitted jobs require separate ownership, provenance, verification, and moderation rules; they are not in the initial release.

## Decision governance

When decisions change, record date, reason, and impact; update affected documents. Inspect the live repository/tests before implementation. Historical Greenhouse-only notes and reports are evidence of prior experiments, not proof of current behavior.

## Decision record — ATS adapter expansion (8 November 2026)

- Greenhouse has been exercised end to end from vacancy extraction through publication to Thungatha, as confirmed by the user. Retain it as the reference adapter and record the exact test evidence in its milestone when available.
- Expand M4 beyond Workday. Implement and validate every ATS already listed in `backend/registry/ats-adapter-registry.json`: Workday, Lever, Breezy HR and Ashby, using the shared adapter contract and the existing company/source workflow.
- Revisit companies and sources already stored in Scout through their configured adapters. Re-extraction must be idempotent and must not create duplicate employers or vacancies.
- `placement_partner` remains a separate recruitment/staffing pipeline, not a direct-employer ATS adapter. Evaluate it separately and do not count agencies toward direct-employer coverage.
- Do not claim an adapter is supported until its public retrieval method, source relationship, access constraints, response completeness and representative live extraction are verified. If a platform cannot be accessed reliably or permissibly, record the limitation rather than fabricating support.
- Docker containerisation is a final packaging milestone after the full application and worker pass local verification. One backend image should support separate API and worker commands; no database container is required.

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
2. Evidence that the employer is a relevant recruitment source for Cape Town roles (for example, a history of Cape Town vacancies); this is not evidence of headquarters or physical presence.
3. Relationship between the employer's official website/careers page and the external source or ATS board.
4. Technical retrieval method and adapter capabilities.
5. Source terms, permission and operational constraints.
6. Human approval to use/publish the source or resulting records.

Evidence supporting one claim does not automatically verify another. In particular, a verified ATS board mapping does not establish employer identity, historical Cape Town recruitment relevance, source permission, adapter implementation readiness or approval.

Unknown capabilities and unverified claims must remain explicitly unknown or pending. Do not infer a capability because an endpoint appears plausible or because one request succeeded. The current registry entries are an initial working dataset; their presence does not mean M1 persistence, schema validation, source approval or production readiness is complete.

### File naming and responsibility

Every file has one clearly defined primary responsibility. Names should state that responsibility clearly and specifically without becoming unnecessarily long. Split independently maintained concepts; do not split a cohesive concept into many files merely to avoid a longer name.

## Decision record — v1 implementation baseline (3 November 2026)

V1 covers the ATS/career-platform catalogue recorded in the adapter registry: Greenhouse, Workday, Lever, Breezy HR and Ashby. Greenhouse is the proven reference flow; the remaining four are to be implemented and validated through the common adapter contract. Recruiter self-service remains out of scope. The private React admin interface is required in v1; it is not a public job-search frontend.

### Product workflow

- The employer is the primary management entity. An employer can have multiple independent recruitment sources; vacancies retain employer and source provenance.
- Add Company is URL-first. The administrator pastes a careers/ATS URL; the backend detects the ATS, inspects the source and extracts employer metadata where reliable. The administrator confirms the employer identity and source relationship before registration.
- Manual ATS selection is a fallback and override. V1 target support includes Greenhouse, Workday, Lever, Breezy HR and Ashby, subject to verified public retrieval methods, source restrictions and representative live tests.
- Adding an employer to an existing adapter is configuration-driven and must not require employer-specific adapter code. A new ATS may require one new adapter implementation.
- Adding a source to an existing employer must not create a duplicate employer. Archiving a source must not remove its employer or other sources.
- Employer/source approval and vacancy approval are separate. Only approved, validated vacancy versions may publish.

### Technical ownership — historical proposal superseded by the implementation stack lock

- Frontend: React + TypeScript + Vite + Tailwind CSS v3.
- Backend: FastAPI (Python) HTTP API with separately executable scheduled/background processing. Keep it provider-portable; hosting is deferred until local implementation is verified.
- Operational persistence: a dedicated Scout Supabase PostgreSQL project. Python owns business rules and authoritative writes; the React client calls the protected backend API.
- Publishing: qualifying records go idempotently to the existing Thungatha Supabase integration. Scout operational state remains separate.
- Keep the application as a simple frontend, backend and database architecture. Do not introduce microservices or provider-specific runtime dependencies without an approved requirement.

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
- Backend: FastAPI (Python) HTTP API with separately executable scheduled/background processing. Keep the backend provider-portable; hosting is deferred until local implementation is verified.
- The current Azure for Students credit is exhausted. Do not upgrade the subscription, create paid Azure resources or assume Azure free allowances will cover persistent storage/compute without a verified cost calculation and explicit user approval.
- Supabase Free may be used for development and a low-volume pilot only after checking current limits, inactivity pausing, backup and production reliability implications. Plan a paid tier or alternative before production depends on uninterrupted service.

### Data retention and storage discipline

- Keep the Scout database focused on structured operational records and the latest meaningful vacancy versions.
- Avoid storing full HTML/page snapshots by default. Retain raw evidence only where it materially supports audit/debugging and apply a bounded retention policy.
- Do not create a new vacancy version for unchanged content.
- Keep extraction run summaries and exception/audit evidence; define retention/archival rules before volume grows.
- Publishing to Thungatha is a one-way, validated, idempotent integration. Scout retains its own operational history.

### Superseded decisions

The following earlier statements are no longer current: Azure Table Storage as mandatory operational persistence; PostgreSQL operational storage hosted as part of the prior Azure-first plan; routine human approval of every vacancy; and a rule that only human-approved vacancy versions can publish. Superseded technical proposals have been replaced in this document with the current React/Vite and FastAPI stack so implementation agents encounter one unambiguous architecture.

## Decision record — implementation stack lock (3 November 2026)

Approved implementation stack: FastAPI backend; React + TypeScript + Vite + Tailwind CSS v3 frontend; Supabase Auth for admin identity. The browser uses only the Supabase URL and publishable/anon key. Backend authorization must independently validate Supabase access tokens and enforce admin permissions. Dedicated Scout Supabase PostgreSQL remains the operational database target; no project was provisioned by this decision. Backend hosting, worker scheduling provider, ORM and migration tooling remain open decisions. No paid resources, hosting, deployment or subscription changes are authorised by this stack decision.

## Decision record — single-admin authentication and deferred hosting (4 November 2026)

### Admin authentication

- Use Supabase Auth for the private Scout admin.
- Only the administrator's explicitly configured email address is permitted to sign in.
- Public registration/sign-up is disabled; there is no public account creation or user onboarding.
- Enforce the email allowlist on the backend for every protected operation. Frontend route guards are only a user-experience measure and are not an authorization boundary.
- The backend independently validates Supabase access tokens and rejects authenticated users whose email is not the configured administrator address.
- Keep the allowlisted email in deployment configuration, not hardcoded in source. Do not expose service-role credentials in the browser.
- Multi-user roles and broader authentication workflows are future scope and are not part of v1.

### Hosting and deployment

- Hosting provider selection is deliberately deferred until the application is implemented and its local functionality has been verified.
- Continue local-first development with a provider-portable FastAPI backend and separately executable scheduled/background processing.
- Do not add provider-specific SDKs, deployment manifests, hosting services or paid resources solely in anticipation of a hosting choice.
- Before release, evaluate the completed application's actual runtime needs, scheduled workload, scraping dependencies, reliability, deployment effort and total cost. Confirm that the chosen provider can run both the HTTP API and unattended processing before committing to it.
- Frontend and backend hosting are separate concerns. The React admin can be deployed independently; the backend hosting decision must account for API execution and automation.
- No hosting provider, paid plan, subscription change or deployment is approved by this decision.

## Decision record — permanent company deletion (5 November 2026)

The administrator has explicitly selected permanent company deletion instead of archival for the Companies screen. This supersedes the earlier instruction to archive employers rather than physically delete them.

- The delete action must clearly identify the company and require explicit confirmation.
- Confirmed deletion removes the employer, its registered sources, extraction-run history and collected vacancies from Scout. Database foreign-key constraints must still be respected; a failed delete must be reported rather than partially completed.
- A deleted company is not recoverable through the UI. If deleted by mistake, the administrator must register it again and re-verify its official sources.
- The confirmation must disclose that linked operational history and vacancies are also deleted.
- This is a deliberate data-retention trade-off: Scout loses the prior extraction and vacancy history for that employer. Do not describe this action as archive or soft delete.

## Decision record — South Africa vacancy persistence boundary (5 November 2026)

The supported vacancy catalogue is South Africa-wide. This supersedes earlier Cape Town-only vacancy relevance and publication statements.

- Employers are managed independently of vacancies. An employer may remain registered and visible with zero currently qualifying South African vacancies.
- A vacancy is persisted only when its location evidence identifies South Africa, a South African province, or a recognized South African city/region.
- A remote vacancy is eligible only when the source explicitly identifies South Africa as the remote location or applicant-eligibility boundary. "Remote" alone is insufficient.
- Missing, ambiguous, or non-South-African location evidence is not persisted as a normal vacancy. It must not enter the published catalogue.
- The geographic gate runs before database upsert, not only in the admin UI or publication stage.
- Existing out-of-scope vacancy rows are removed by migration 0005. Employer and source records are retained.
- Location matching is deliberately conservative. False negatives should be reviewed and the allow-list expanded with evidence; unknown locations must not be assumed South African.
- This rule applies to every adapter through the shared persistence boundary. Adapter-specific checks may add validation but must not weaken it.
- The admin South Africa filter is a view over the already-qualified vacancy catalogue, not a substitute for ingestion validation.

## Decision record — export location scope (6 November 2026)

- Vacancy export defaults to `south_africa`, matching the South Africa-wide persisted vacancy catalogue.
- Export accepts the same location scopes as the admin vacancy view: `cape_town`, `western_cape`, and `south_africa`.
- The selected scope filters the export query itself, including its total count and returned page. Changing the admin location filter must be reflected when the corresponding export is requested.
- `all` remains an accepted compatibility value and does not add a geographic predicate; ingestion already limits the persisted catalogue to South African vacancies.
- This is an export/read-scope decision only. It does not change the South Africa ingestion boundary or delete broader South African records.

## Decision record — Greenhouse office-level location mapping (6 November 2026)

- When a Greenhouse vacancy has a broad country/province location label and one or more specific office names, Scout uses the office names as the primary location evidence instead of displaying the broad label.
- Generic operational suffixes such as DC, Office, Hub, Distribution Centre, Cross Dock Facility, Facility and Warehouse are removed from the display location when a place name precedes them. Equivalent office labels such as "Cape Town DC" and "Cape Town Office" therefore resolve to the same display location, "Cape Town".
- Distinct office locations remain distinct; this mapping does not choose one arbitrarily when multiple places are attached to a vacancy.
- A specific job-level location is retained when it is already more precise than a broad office label.
- Original Greenhouse location, department and office objects remain in `raw_payload` for traceability.
- This is source-field prioritisation and display normalization, not a general geocoder. It must not infer a city from employer headquarters or unrelated description text. Unknown or ambiguous office labels require a later evidence-based resolution step.

## Decision record — vacancy freshness date priority (6 November 2026)

- Vacancy freshness represents the employer/source's latest recorded activity on the advertisement, not the date Scout first discovered it.
- Use `source_updated_at` as the primary freshness timestamp when it is present and valid.
- If `source_updated_at` is absent or invalid, fall back to the original `published_at` timestamp.
- If neither timestamp is valid, display `Date unavailable`. Do not substitute `first_seen_at`, `last_seen_at`, or Scout's database timestamps because those describe Scout's observation activity, not the employer's advertisement date.
- Preserve `published_at` and `source_updated_at` independently. Updating freshness must never overwrite the original publication timestamp.
- Admin freshness bands: 0–7 days green (Fresh), 8–14 days yellow (Recent), 15–30 days amber (Aging), and over 30 days red (Stale).
- Freshness is an activity signal, not proof that a vacancy remains open or that an employer has not hired. Age alone must not expire, remove, or suppress a vacancy.
- Show the selected timestamp's date and relative age in the vacancy list and detail header.

## Decision record — twice-daily vacancy extraction window (8 November 2026)

- Replace the earlier eight-hour vacancy extraction cadence with two scheduled starts per day: 06:00 and 18:00 South African time (`Africa/Johannesburg`).
- Each scheduled run has a maximum duration of one hour, ending no later than 07:00 or 19:00 respectively.
- One hour is a ceiling, not a required runtime. The worker exits as soon as its assigned work is complete; a 15-minute or 30-minute run is successful when all assigned work has completed.
- Do not pad, sleep, or otherwise force a run to consume the full hour.
- Prevent overlapping executions. If a run reaches the one-hour limit, record it as timed out/partial as appropriate and preserve completed per-source progress. Never treat a timeout or incomplete inventory as evidence that vacancies have disappeared.
- This is the initial operating schedule; actual runtimes and source coverage will be measured after the complete extraction workflow is implemented and tested. The schedule and maximum duration remain configurable.

## Decision record — expanded ATS and career-platform coverage (8 November 2026)

The earlier five-platform M4 scope is superseded by the research catalogue in `docs/ATS-PLATFORM-RESEARCH.md` and `backend/registry/ats-adapter-registry.json`.

- Keep all researched platforms and candidate employer sources in scope. Implementation difficulty changes sequencing, not employer eligibility or discovery coverage.
- First-wave priorities are Ashby, Lever, Teamtailor RSS, Personio XML, Recruitee XML and Workable's observed public widget. Greenhouse remains the proven reference adapter and receives reliability/evidence closure.
- Second wave: SmartRecruiters, BambooHR and Breezy HR. Third wave: Simplify.hr, eRecruit/Neptune investigation, Zoho Recruit and SAP SuccessFactors. Workday is deferred from active investigation and implementation until further notice.
- Placement Partner remains in scope as a separate recruitment-agency source pipeline. Validate redirect chains and final candidate destinations; accept redirects only when they preserve the exact vacancy/application journey.
- JobAdder is partner/customer-authorised unless a separate public source is verified. Leaply is a discovery lead, not a confirmed public ATS adapter.
- Personio and Workable are added candidates beyond the original supplied list because research found useful public vacancy retrieval routes.
- Company names supplied as ATS examples remain discovery leads until the employer's own careers page establishes the platform relationship. A company may have multiple sources and multiple ATS platforms.
- Do not use undocumented endpoints as if they were vendor-supported APIs. Record access method, source evidence, field completeness, redirect behavior and operational limits separately.
- The research ranking is an implementation-effort estimate, not a market-share ranking. High-value difficult sources must not be excluded; move them into the hard-source backlog and revisit based on employer coverage.

## Decision record — first-wave employer test cohort and Workday deferral (8 November 2026)

- The first-wave research cohort is Ashby, Lever, Teamtailor, Personio, Recruitee and Workable. Greenhouse remains the already-implemented reference adapter and is not part of this new research cohort.
- Company names and career-page URLs for at least three candidate employers per first-wave ATS are recorded in `backend/registry/ats-adapter-registry.json`, `docs/ATS-PLATFORM-RESEARCH.md` and the companion JSONC test-target file.
- These company URLs are research targets, not proof that the proposed public endpoint/feed is enabled or that extraction has succeeded. Verify the actual career page, redirects, network requests, listing/detail retrieval, pagination and vacancy-specific application URL for each employer.
- Workday is deferred from active research, implementation and test-target lists until further notice. Its previous CXS research is retained only as historical context; do not allocate current M4 work to Workday unless the user reactivates it.
- Greenhouse is excluded from the new company cohort because its adapter is already implemented; outstanding Greenhouse reliability/acceptance work remains tracked separately.
