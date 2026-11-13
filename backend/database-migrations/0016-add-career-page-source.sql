ALTER TABLE employer_sources
    DROP CONSTRAINT employer_sources_adapter_key_check;

ALTER TABLE employer_sources
    ADD CONSTRAINT employer_sources_adapter_key_check
    CHECK (adapter_key IN (
        'career_page', 'greenhouse', 'lever', 'teamtailor', 'workable', 'workday'
    ));
