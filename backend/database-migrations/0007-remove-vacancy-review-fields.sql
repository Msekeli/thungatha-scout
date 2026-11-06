-- Vacancy review was removed. Manual vacancy lifecycle is archive/reinstate only.
DROP INDEX IF EXISTS vacancies_review_status_idx;

ALTER TABLE vacancies
    DROP COLUMN IF EXISTS review_status,
    DROP COLUMN IF EXISTS review_reason,
    DROP COLUMN IF EXISTS reviewed_at;
