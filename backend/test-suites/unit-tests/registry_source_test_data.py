from registry_importer_test_connection import FakeConnection


def registry_for(url: str, config: dict) -> dict:
    return {"employers": [{
        "name": "Example Employer",
        "sources": [{"ats": "greenhouse", "official_source_url": url, "config": config}],
    }]}


def add_source(connection: FakeConnection, slug: str) -> dict:
    employer_id = connection.employers[-1]["id"]
    url = f"https://job-boards.greenhouse.io/{slug}"
    source = {
        "id": slug, "employer_id": employer_id, "adapter_key": "greenhouse",
        "source_url": url, "normalized_url": url, "adapter_config": {"slug": slug},
    }
    connection.sources.append(source)
    return source
