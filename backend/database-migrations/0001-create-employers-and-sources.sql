CREATE TABLE employers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL CHECK (length(btrim(name)) > 0),
    legal_name TEXT,
    website_url TEXT,
    organization_type TEXT NOT NULL DEFAULT 'unresolved'
        CHECK (organization_type IN (
            'direct_employer',
            'recruitment_agency',
            'staffing_company',
            'hybrid',
            'other',
            'unresolved'
        )),
    status TEXT NOT NULL DEFAULT 'discovered'
        CHECK (status IN (
            'discovered',
            'pending_review',
            'approved',
            'rejected',
            'needs_review',
            'inactive'
        )),
    city TEXT,
    province TEXT,
    country TEXT,
    identity_evidence JSONB NOT NULL DEFAULT '[]'::jsonb
        CHECK (jsonb_typeof(identity_evidence) = 'array'),
    location_evidence JSONB NOT NULL DEFAULT '[]'::jsonb
        CHECK (jsonb_typeof(location_evidence) = 'array'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE employer_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employer_id UUID NOT NULL REFERENCES employers(id) ON DELETE RESTRICT,
    adapter_key TEXT NOT NULL
        CHECK (adapter_key IN ('greenhouse', 'workday')),
    source_url TEXT NOT NULL CHECK (length(btrim(source_url)) > 0),
    normalized_url TEXT NOT NULL UNIQUE
        CHECK (length(btrim(normalized_url)) > 0),
    adapter_config JSONB NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(adapter_config) = 'object'),
    status TEXT NOT NULL DEFAULT 'discovered'
        CHECK (status IN (
            'discovered',
            'pending_verification',
            'verified',
            'temporarily_unavailable',
            'invalid',
            'needs_review',
            'inactive'
        )),
    permission_status TEXT NOT NULL DEFAULT 'unknown'
        CHECK (permission_status IN (
            'unknown',
            'allowed',
            'restricted',
            'needs_review'
        )),
    relationship_evidence JSONB NOT NULL DEFAULT '[]'::jsonb
        CHECK (jsonb_typeof(relationship_evidence) = 'array'),
    verified_at TIMESTAMPTZ,
    last_checked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX employer_sources_employer_id_idx
    ON employer_sources (employer_id);

CREATE INDEX employers_status_idx
    ON employers (status);

CREATE INDEX employer_sources_status_idx
    ON employer_sources (status);
