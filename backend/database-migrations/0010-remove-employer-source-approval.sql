-- Remove company/source approval and verification. Keep last_checked_at for operational source previews.
ALTER TABLE employers
    DROP CONSTRAINT IF EXISTS employers_status_check,
    DROP COLUMN IF EXISTS status,
    DROP COLUMN IF EXISTS identity_evidence,
    DROP COLUMN IF EXISTS location_evidence;

DROP INDEX IF EXISTS employers_status_idx;

ALTER TABLE employer_sources
    DROP CONSTRAINT IF EXISTS employer_sources_status_check,
    DROP CONSTRAINT IF EXISTS employer_sources_permission_status_check,
    DROP COLUMN IF EXISTS status,
    DROP COLUMN IF EXISTS permission_status,
    DROP COLUMN IF EXISTS relationship_evidence,
    DROP COLUMN IF EXISTS verified_at;

DROP INDEX IF EXISTS employer_sources_status_idx;
