-- Best-effort logo backfill. Prefer an employer's own website domain.
-- Do not assign ATS platform favicons as employer branding.
WITH logo_candidates AS (
    SELECT
        e.id,
        COALESCE(
            NULLIF(regexp_replace(e.website_url, '^https?://([^/:?#]+).*$', '\\1'), e.website_url),
            (
                SELECT NULLIF(
                    regexp_replace(s.employer_careers_url, '^https?://([^/:?#]+).*$', '\\1'),
                    s.employer_careers_url
                )
                FROM employer_sources s
                WHERE s.employer_id = e.id
                  AND s.employer_careers_url IS NOT NULL
                  AND lower(regexp_replace(s.employer_careers_url, '^https?://([^/:?#]+).*$', '\\1'))
                      NOT IN ('boards.greenhouse.io', 'job-boards.greenhouse.io', 'jobs.lever.co', 'jobs.eu.lever.co')
                  AND lower(regexp_replace(s.employer_careers_url, '^https?://([^/:?#]+).*$', '\\1'))
                      NOT LIKE '%.teamtailor.com'
                ORDER BY s.created_at
                LIMIT 1
            )
        ) AS domain,
        e.website_url
    FROM employers e
    WHERE e.logo_url IS NULL
)
UPDATE employers e
SET logo_url = 'https://www.google.com/s2/favicons?domain=' || c.domain || '&sz=128',
    logo_source_url = COALESCE(c.website_url, 'https://' || c.domain)
FROM logo_candidates c
WHERE e.id = c.id
  AND c.domain IS NOT NULL
  AND c.domain <> ''
  AND c.domain !~ '[^a-zA-Z0-9.-]';
