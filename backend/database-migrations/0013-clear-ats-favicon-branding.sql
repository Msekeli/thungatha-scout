-- Remove ATS platform favicons and generic favicon-service URLs.
-- Logo discovery will repopulate only URLs found in employer branding metadata.
UPDATE employers
SET logo_url = NULL,
    logo_source_url = NULL,
    updated_at = NOW()
WHERE logo_url ILIKE 'https://www.google.com/s2/favicons%'
   OR logo_url ILIKE 'https://favicons.githubusercontent.com%'
   OR lower(logo_source_url) LIKE '%jobs.lever.co%'
   OR lower(logo_source_url) LIKE '%greenhouse.io%'
   OR lower(logo_source_url) LIKE '%.teamtailor.com%';
