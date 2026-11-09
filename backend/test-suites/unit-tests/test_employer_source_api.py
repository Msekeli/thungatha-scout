from uuid import uuid4

from scout.api.employers import get_employer_service
from employer_api_test_doubles import FakeEmployerService, client_for


def test_employer_source_api_rejects_mismatched_employer_ids() -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append({"id": str(employer_id), "name": "Example"})
    with client_for(get_employer_service, service) as client:
        response = client.post(
            f"/api/v1/employers/{employer_id}/sources",
            json={
                "employer_id": str(uuid4()), "adapter_key": "greenhouse",
                "source_url": "https://boards.greenhouse.io/example",
                "normalized_url": "https://boards.greenhouse.io/example",
                "adapter_config": {"slug": "example"},
            },
        )
    assert response.status_code == 422


def test_employer_source_api_registers_source_without_approval_state() -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append({"id": str(employer_id), "name": "Example"})
    with client_for(get_employer_service, service) as client:
        response = client.post(
            f"/api/v1/employers/{employer_id}/sources",
            json={
                "employer_id": str(employer_id), "adapter_key": "greenhouse",
                "source_url": "https://boards.greenhouse.io/example",
                "normalized_url": "https://boards.greenhouse.io/example",
                "adapter_config": {"slug": "example"},
            },
        )
    assert response.status_code == 201
    assert response.json()["adapter_key"] == "greenhouse"
    assert "status" not in response.json()


def test_bulk_source_endpoint_returns_all_registered_sources() -> None:
    service = FakeEmployerService()
    service.sources.append({"id": "source-1", "employer_id": "employer-1",
                            "adapter_key": "greenhouse"})
    with client_for(get_employer_service, service) as client:
        response = client.get("/api/v1/employers/sources")
    assert response.status_code == 200
    assert response.json() == service.sources


def test_employer_source_api_accepts_lever_configuration() -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append({"id": str(employer_id), "name": "Mama Money"})
    with client_for(get_employer_service, service) as client:
        response = client.post(
            f"/api/v1/employers/{employer_id}/sources",
            json={
                "employer_id": str(employer_id), "adapter_key": "lever",
                "source_url": "https://jobs.lever.co/mamamoney",
                "normalized_url": "https://jobs.lever.co/mamamoney",
                "adapter_config": {"slug": "mamamoney", "region": "global"},
            },
        )
    assert response.status_code == 201
    assert response.json()["adapter_key"] == "lever"
    assert "permission_status" not in response.json()
