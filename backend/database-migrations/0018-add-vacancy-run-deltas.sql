ALTER TABLE extraction_runs
    ADD COLUMN jobs_added INTEGER NOT NULL DEFAULT 0
        CHECK (jobs_added >= 0),
    ADD COLUMN jobs_missing INTEGER NOT NULL DEFAULT 0
        CHECK (jobs_missing >= 0),
    ADD COLUMN is_baseline BOOLEAN NOT NULL DEFAULT FALSE;
