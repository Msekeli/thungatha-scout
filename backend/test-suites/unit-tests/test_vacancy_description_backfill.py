from scout.maintenance.sanitize_existing_vacancy_descriptions import (
    prepare_changes,
)


def test_backfill_only_returns_changed_descriptions() -> None:
    rows = [
        {"id": "1", "description": "<p style='color:red'>Build.</p>"},
        {"id": "2", "description": "<p>Already clean.</p>"},
        {"id": "3", "description": None},
    ]
    changes = prepare_changes(rows)
    assert len(changes) == 1
    assert changes[0][0] == "1"
    assert changes[0][2] == "<p>Build.</p>"
