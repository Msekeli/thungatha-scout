ALTER TABLE employers
    ADD COLUMN logo_url TEXT,
    ADD COLUMN logo_source_url TEXT;

ALTER TABLE vacancies
    ADD COLUMN review_status TEXT NOT NULL DEFAULT 'pending'
        CHECK (review_status IN (
            'pending', 'needs_verification', 'verified', 'rejected'
        )),
    ADD COLUMN review_reason TEXT,
    ADD COLUMN reviewed_at TIMESTAMPTZ,
    ADD COLUMN archived_at TIMESTAMPTZ,
    ADD COLUMN archived_reason TEXT;

UPDATE vacancies
SET review_status = 'needs_verification',
    review_reason = CASE
        WHEN location_text IS NULL OR btrim(location_text) = ''
            THEN 'Location is missing from the source.'
        WHEN lower(location_text) LIKE '%remote%'
            THEN 'Remote-work location and geographic eligibility need verification.'
        ELSE 'Confirm that this South African location is within the supported scope.'
    END
WHERE location_text IS NULL
   OR lower(location_text) LIKE '%south africa%'
   OR lower(location_text) LIKE '%remote%';

CREATE INDEX vacancies_review_status_idx
    ON vacancies (review_status, created_at DESC)
    WHERE archived_at IS NULL;
CREATE INDEX vacancies_archived_at_idx
    ON vacancies (archived_at)
    WHERE archived_at IS NOT NULL;
CREATE INDEX employers_logo_url_idx
    ON employers (id)
    WHERE logo_url IS NOT NULL;
