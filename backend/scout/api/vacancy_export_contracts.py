from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VacancyExportRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scout_vacancy_id: UUID
    employer_name: str
    logo_url: str | None
    title: str
    description: str
    location_text: str | None
    application_url: str
    published_at: datetime | None
    source_updated_at: datetime | None
    first_seen_at: datetime


class VacancyExportPage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[VacancyExportRecord]
    total: int
    limit: int
    offset: int
    has_more: bool
    location_scope: str
