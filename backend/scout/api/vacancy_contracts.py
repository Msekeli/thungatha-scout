from pydantic import BaseModel, Field


class VacancyArchiveRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)
