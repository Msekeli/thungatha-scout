ALTER TABLE extraction_runs
    DROP CONSTRAINT extraction_runs_outcome_check;

ALTER TABLE extraction_runs
    ADD CONSTRAINT extraction_runs_outcome_check
    CHECK (outcome IN (
        'running', 'success', 'empty', 'partial', 'not_found',
        'blocked', 'rate_limited', 'transient_failure', 'malformed',
        'persistence_failure'
    ));
