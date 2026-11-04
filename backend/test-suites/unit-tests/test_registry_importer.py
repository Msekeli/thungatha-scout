from uuid import uuid4

from scout.registry_importer import import_registry


class FakeResult:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self):
        self.employers = []
        self.sources = []

    def execute(self, query, params=()):
        if "SELECT id, website_url FROM employers" in query:
            row = next(
                (item for item in self.employers if item["name"] == params[0]),
                None,
            )
            return FakeResult(row)
        if "INSERT INTO employers" in query:
            row = {
                "id": uuid4(),
                "name": params[0],
                "website_url": params[1],
            }
            self.employers.append(row)
            return FakeResult(row)
        if "SELECT id, employer_id, adapter_key" in query:
            row = next(
                (
                    item for item in self.sources
                    if item["normalized_url"] == params[0]
                ),
                None,
            )
            return FakeResult(row)
        if "INSERT INTO employer_sources" in query:
            self.sources.append({
                "id": uuid4(),
                "employer_id": params[0],
                "adapter_key": params[1],
                "normalized_url": params[4],
            })
            return FakeResult()
        raise AssertionError(f"Unexpected SQL: {query}")


def test_registry_import_creates_employers_and_supported_sources_once() -> None:
    registry = {
        "employers": [
            {
                "name": "Example Employer",
                "careers_url": "https://example.com/careers",
                "organization_classification": "direct_employer",
                "cape_town_presence_claimed": True,
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": "https://job-boards.greenhouse.io/example",
                        "config": {"slug": "example"},
                        "verification_evidence": [
                            "https://example.com/careers"
                        ],
                    },
                    {
                        "ats": "placement_partner",
                        "official_source_url": "https://placementpartner.example",
                    },
                ],
            }
        ]
    }
    connection = FakeConnection()

    first = import_registry(registry, connection)
    second = import_registry(registry, connection)

    assert first == {
        "employers_created": 1,
        "sources_created": 1,
        "sources_skipped": 1,
    }
    assert second == {
        "employers_created": 0,
        "sources_created": 0,
        "sources_skipped": 1,
    }
    assert len(connection.employers) == 1
    assert len(connection.sources) == 1
