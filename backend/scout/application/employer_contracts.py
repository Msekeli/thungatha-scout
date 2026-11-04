from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

OrganizationType = Literal[
    "direct_employer",
    "recruitment_agency",
    "staffing_company",
    "hybrid",
    "other",
    "unresolved",
]


class EmployerCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    legal_name: str | None = None
    website_url: HttpUrl | None = None
    organization_type: OrganizationType = "unresolved"
    city: str | None = None
    province: str | None = None
    country: str | None = None
    identity_evidence: list[dict[str, Any]] = Field(default_factory=list)
    location_evidence: list[dict[str, Any]] = Field(default_factory=list)


class EmployerBrandingUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    logo_url: HttpUrl | None = None
    logo_source_url: HttpUrl | None = None


class EmployerSourceCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    employer_id: UUID
    adapter_key: Literal["greenhouse", "workday"]
    source_url: HttpUrl
    employer_careers_url: HttpUrl | None = None
    normalized_url: HttpUrl
    adapter_config: dict[str, Any] = Field(default_factory=dict)
    relationship_evidence: list[dict[str, Any]] = Field(default_factory=list)
