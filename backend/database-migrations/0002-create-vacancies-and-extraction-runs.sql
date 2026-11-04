CREATE TABLE extraction_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES employer_sources(id) ON DELETE RESTRICT,
    outcome TEXT NOT NULL CHECK (outcome IN (
        'running', 'success', 'empty', 'partial', 'not_found',
        'blocked', 'rate_limited', 'transient_failure', 'malformed'
    )),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    jobs_received INTEGER NOT NULL DEFAULT 0 CHECK (jobs_received >= 0),
    jobs_inserted INTEGER NOT NULL DEFAULT 0 CHECK (jobs_inserted >= 0),
    jobs_updated INTEGER NOT NULL DEFAULT 0 CHECK (jobs_updated >= 0),
    detail TEXT,
    complete BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE vacancies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employer_id UUID NOT NULL REFERENCES employers(id) ON DELETE RESTRICT,
    source_id UUID NOT NULL REFERENCES employer_sources(id) ON DELETE RESTRICT,
    external_job_id TEXT NOT NULL CHECK (length(btrim(external_job_id)) > 0),
    title TEXT NOT NULL CHECK (length(btrim(title)) > 0),
    description TEXT,
    location_text TEXT,
    department TEXT,
    office TEXT,
    source_url TEXT NOT NULL,
    application_url TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    source_updated_at TIMESTAMPTZ,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN (
            'active', 'possibly_expired', 'expired', 'removed',
            'unavailable', 'needs_review'
        )),
    raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(raw_payload) = 'object'),
    content_fingerprint TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT vacancies_source_external_id_unique
        UNIQUE (source_id, external_job_id)
);

CREATE INDEX vacancies_employer_status_idx
    ON vacancies (employer_id, status);
CREATE INDEX vacancies_source_status_idx
    ON vacancies (source_id, status);
CREATE INDEX extraction_runs_source_started_idx
    ON extraction_runs (source_id, started_at DESC);
