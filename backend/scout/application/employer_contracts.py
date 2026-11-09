from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

OrganizationType = Literal[
    "direct_employer", "recruitment_agency", "staffing_company",
    "hybrid", "other", "unresolved",
]


class EmployerCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1)
    legal_name: str | None = None
    website_url: HttpUrl | None = None
    logo_url: HttpUrl | None = None
    logo_source_url: HttpUrl | None = None
    organization_type: OrganizationType = "unresolved"
    city: str | None = None
    province: str | None = None
    country: str | None = None


class EmployerUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1)
    legal_name: str | None = None
    website_url: HttpUrl | None = None
    organization_type: OrganizationType = "unresolved"
    city: str | None = None
    province: str | None = None
    country: str | None = None


class EmployerBrandingUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    logo_url: HttpUrl | None = None
    logo_source_url: HttpUrl | None = None


class DiscoveryPreviewJob(BaseModel):
    id: str | int
    title: str = Field(min_length=1, max_length=300)
    absolute_url: HttpUrl | None = None
    location: dict[str, str | None] | None = None


class SourceDiscoveryPreview(BaseModel):
    total_vacancies: int = Field(ge=0)
    jobs: list[DiscoveryPreviewJob] = Field(default_factory=list, max_length=5)


class EmployerSourceCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    employer_id: UUID
    adapter_key: Literal["greenhouse", "lever", "workday"]
    source_url: HttpUrl
    employer_careers_url: HttpUrl | None = None
    normalized_url: HttpUrl
    adapter_config: dict[str, Any] = Field(default_factory=dict)
    discovery_preview: SourceDiscoveryPreview | None = None
