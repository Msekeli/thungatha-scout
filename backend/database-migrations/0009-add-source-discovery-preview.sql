ALTER TABLE employer_sources
ADD COLUMN discovery_preview JSONB
    CHECK (
        discovery_preview IS NULL
        OR jsonb_typeof(discovery_preview) = 'object'
    );
