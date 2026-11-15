from scout.registry_importer import import_registry
from registry_importer_test_connection import FakeConnection


def _employer_registry(name: str, careers_url: str) -> dict:
    slug = name.lower().replace(" ", "-")
    return {
        "employers": [
            {
                "name": name,
                "careers_url": careers_url,
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": f"https://job-boards.greenhouse.io/{slug}",
                        "config": {"slug": slug},
                    }
                ],
            }
        ]
    }


def test_new_employer_import_does_not_create_presence_evidence() -> None:
    connection = FakeConnection()
    result = import_registry(
        _employer_registry("Example Employer", "https://example.com/careers"),
        connection,
    )
    assert result["employers_created"] == 1
    assert "location_evidence" not in connection.employers[0]


def test_existing_employer_with_different_website_is_preserved() -> None:
    connection = FakeConnection()
    connection.employers.append(
        {
            "id": "existing-id",
            "name": "Example Employer",
            "website_url": "https://different.example.com/careers",
        }
    )
    result = import_registry(
        _employer_registry("Example Employer", "https://example.com/careers"),
        connection,
    )
    assert result["employers_created"] == 0
    assert result["employers_updated"] == 0
    assert (
        connection.employers[0]["website_url"]
        == "https://different.example.com/careers"
    )


def test_existing_employer_without_website_gets_registry_careers_url() -> None:
    connection = FakeConnection()
    connection.employers.append(
        {
            "id": "existing-id",
            "name": "Example Employer",
            "website_url": None,
        }
    )
    result = import_registry(
        _employer_registry("Example Employer", "https://example.com/careers"),
        connection,
    )
    assert result["employers_created"] == 0
    assert result["employers_updated"] == 1
    assert connection.employers[0]["website_url"] == "https://example.com/careers"


def test_existing_employer_name_matching_ignores_case() -> None:
    connection = FakeConnection()
    connection.employers.append(
        {
            "id": "existing-digioutsource-id",
            "name": "Digioutsource",
            "website_url": "https://supergroup.com",
        }
    )
    result = import_registry(
        _employer_registry("DigiOutsource", "https://supergroup.com/careers"),
        connection,
    )
    assert result["employers_created"] == 0
    assert result["employers_updated"] == 0
    assert len(connection.employers) == 1
    assert connection.employers[0]["id"] == "existing-digioutsource-id"
