from uuid import uuid4

from scout.api.employer_api_dependencies import get_employer_source_update_service
from employer_api_test_doubles import FakeEmployerSourceUpdateService, client_for


def test_employer_source_api_updates_configuration() -> None:
    service = FakeEmployerSourceUpdateService()
    employer_id, source_id = uuid4(), uuid4()
    with client_for(get_employer_source_update_service, service) as client:
        response = client.put(
            f"/api/v1/employers/{employer_id}/sources/{source_id}",
            json={
                "adapter_key": "greenhouse",
                "source_url": "https://job-boards.greenhouse.io/impact",
                "normalized_url": "https://job-boards.greenhouse.io/impact",
                "adapter_config": {"slug": "impact"},
            },
        )
    assert response.status_code == 200
    assert response.json()["adapter_config"] == {"slug": "impact"}
    assert service.updated[:2] == (employer_id, source_id)


def test_employer_source_api_rejects_invalid_adapter_configuration() -> None:
    service = FakeEmployerSourceUpdateService()
    with client_for(get_employer_source_update_service, service) as client:
        response = client.put(
            f"/api/v1/employers/{uuid4()}/sources/{uuid4()}",
            json={
                "adapter_key": "greenhouse",
                "source_url": "https://job-boards.greenhouse.io/impact",
                "normalized_url": "https://job-boards.greenhouse.io/impact",
                "adapter_config": {"slug": ""},
            },
        )
    assert response.status_code == 422
    assert service.updated is None


def test_employer_source_api_updates_workable_configuration() -> None:
    service = FakeEmployerSourceUpdateService()
    employer_id, source_id = uuid4(), uuid4()
    with client_for(get_employer_source_update_service, service) as client:
        response = client.put(
            f"/api/v1/employers/{employer_id}/sources/{source_id}",
            json={
                "adapter_key": "workable",
                "source_url": "https://apply.workable.com/lekkeslaap",
                "normalized_url": "https://apply.workable.com/lekkeslaap",
                "adapter_config": {"slug": "lekkeslaap"},
            },
        )
    assert response.status_code == 200
    assert response.json()["adapter_key"] == "workable"
