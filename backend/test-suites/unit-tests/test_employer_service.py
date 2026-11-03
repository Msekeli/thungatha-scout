from uuid import uuid4

import pytest
from pydantic import ValidationError

from scout.application.employer_service import (
    EmployerCreate,
    EmployerSourceCreate,
)


def test_employer_defaults_to_unresolved_and_discovered() -> None:
    employer = EmployerCreate(name="  Example Employer  ")

    assert employer.name == "Example Employer"
    assert employer.organization_type == "unresolved"


def test_employer_rejects_blank_name() -> None:
    with pytest.raises(ValidationError):
        EmployerCreate(name="   ")


def test_source_accepts_only_supported_v1_adapters() -> None:
    with pytest.raises(ValidationError):
        EmployerSourceCreate(
            employer_id=uuid4(),
            adapter_key="lever",
            source_url="https://jobs.example.com",
            normalized_url="https://jobs.example.com",
        )


def test_creation_payloads_cannot_set_review_or_permission_state() -> None:
    employer = EmployerCreate(name="Example Employer", status="approved")
    source = EmployerSourceCreate(
        employer_id=uuid4(),
        adapter_key="greenhouse",
        source_url="https://boards.greenhouse.io/example",
        normalized_url="https://boards.greenhouse.io/example",
        status="verified",
        permission_status="allowed",
    )

    assert "status" not in employer.model_dump()
    assert "status" not in source.model_dump()
    assert "permission_status" not in source.model_dump()
