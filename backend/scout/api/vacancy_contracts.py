from typing import Literal

from pydantic import BaseModel, Field


class VacancyReviewUpdate(BaseModel):
    review_status: Literal["pending", "needs_verification", "verified", "rejected"]
    review_reason: str | None = Field(default=None, max_length=2000)


class VacancyArchiveRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)
