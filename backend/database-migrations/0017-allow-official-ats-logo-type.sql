ALTER TABLE employers
    DROP CONSTRAINT employers_logo_type_check;

ALTER TABLE employers
    ADD CONSTRAINT employers_logo_type_check
    CHECK (logo_type IN (
        'official_logo',
        'official_ats_logo',
        'official_favicon',
        'careers_favicon',
        'unverified'
    ));
