from uuid import uuid4

from scout.api.employers import get_employer_service
from employer_api_test_doubles import FakeEmployerService, client_for


def test_employer_source_api_accepts_workable_configuration() -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append({"id": str(employer_id), "name": "LekkeSlaap"})
    with client_for(get_employer_service, service) as client:
        response = client.post(
            f"/api/v1/employers/{employer_id}/sources",
            json={
                "employer_id": str(employer_id),
                "adapter_key": "workable",
                "source_url": "https://apply.workable.com/lekkeslaap",
                "normalized_url": "https://apply.workable.com/lekkeslaap",
                "employer_careers_url": "https://apply.workable.com/lekkeslaap/",
                "adapter_config": {"slug": "lekkeslaap"},
            },
        )
    assert response.status_code == 201
    assert response.json()["adapter_key"] == "workable"


def test_validation_error_includes_invalid_field_details() -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append({"id": str(employer_id), "name": "Example"})
    with client_for(get_employer_service, service) as client:
        response = client.post(
            f"/api/v1/employers/{employer_id}/sources",
            json={
                "employer_id": str(employer_id),
                "adapter_key": "workable",
                "source_url": "not-a-url",
                "normalized_url": "https://apply.workable.com/example",
                "adapter_config": {"slug": "example"},
            },
        )
    assert response.status_code == 422
    assert "source_url" in response.json()["detail"]
