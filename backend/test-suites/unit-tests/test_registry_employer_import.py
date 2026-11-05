import pytest

from scout.registry_importer import import_registry
from registry_importer_test_connection import FakeConnection


def test_new_employer_keeps_location_claim_pending_review() -> None:
    connection = FakeConnection()
    result = import_registry(
        {
            "employers": [
                {
                    "name": "Example Employer",
                    "careers_url": "https://example.com/careers",
                    "cape_town_presence_claimed": True,
                }
            ]
        },
        connection,
    )

    assert result["employers_created"] == 1
    assert connection.employers[0]["location_evidence"] == [
        {"claim": "Cape Town presence", "status": "pending_verification"}
    ]


def test_existing_employer_with_different_website_is_rejected() -> None:
    connection = FakeConnection()
    connection.employers.append(
        {
            "id": "existing-id",
            "name": "Example Employer",
            "website_url": "https://different.example.com/careers",
        }
    )
    registry = {
        "employers": [
            {"name": "Example Employer", "careers_url": "https://example.com/careers"}
        ]
    }

    with pytest.raises(ValueError, match="another website"):
        import_registry(registry, connection)
