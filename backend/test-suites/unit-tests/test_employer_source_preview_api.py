from uuid import uuid4

from scout.api.employers import get_employer_service
from employer_api_test_doubles import FakeEmployerService, client_for


def test_source_preview_is_saved_without_approval_fields() -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append({"id": str(employer_id), "name": "Example"})
    preview = {
        "total_vacancies": 12,
        "jobs": [{
            "id": "job-1", "title": "Software Engineer",
            "absolute_url": "https://jobs.example.com/job-1",
            "location": {"name": "Cape Town"}, "content": "Build software.",
        }],
    }
    with client_for(get_employer_service, service) as client:
        response = client.post(
            f"/api/v1/employers/{employer_id}/sources",
            json={
                "employer_id": str(employer_id), "adapter_key": "lever",
                "source_url": "https://jobs.lever.co/example",
                "normalized_url": "https://jobs.lever.co/example",
                "adapter_config": {"slug": "example", "region": "global"},
                "discovery_preview": preview,
            },
        )
    assert response.status_code == 201
    assert response.json()["discovery_preview"]["total_vacancies"] == 12
    assert "status" not in response.json()
    assert "permission_status" not in response.json()
