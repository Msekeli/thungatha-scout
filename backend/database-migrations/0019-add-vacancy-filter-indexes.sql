CREATE INDEX vacancies_active_effective_date_idx
    ON vacancies ((COALESCE(source_updated_at, published_at)) DESC)
    WHERE status = 'active' AND archived_at IS NULL;

CREATE INDEX vacancies_active_first_seen_idx
    ON vacancies (first_seen_at DESC)
    WHERE status = 'active' AND archived_at IS NULL;

CREATE INDEX vacancies_active_employer_effective_date_idx
    ON vacancies (
        employer_id,
        (COALESCE(source_updated_at, published_at)) DESC
    )
    WHERE status = 'active' AND archived_at IS NULL;
