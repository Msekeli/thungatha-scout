-- Descriptions and normalized fields already have dedicated columns.
-- Remove duplicate copies from the retained source payload to reduce row size.
UPDATE vacancies
SET raw_payload = raw_payload - ARRAY[
    'content',
    'title',
    'absolute_url',
    'updated_at',
    'first_published'
]
WHERE raw_payload ? 'content';
