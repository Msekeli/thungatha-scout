-- Track the provenance of employer branding assets.
-- Existing records are deliberately unverified until their source is audited.
ALTER TABLE employers
    ADD COLUMN logo_type TEXT NOT NULL DEFAULT 'unverified'
    CHECK (logo_type IN (
        'official_logo',
        'official_favicon',
        'careers_favicon',
        'unverified'
    ));

COMMENT ON COLUMN employers.logo_type IS
    'Provenance classification for logo_url; unverified assets must not be rendered as employer branding.';
