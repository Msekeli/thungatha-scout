from typing import Literal

from pydantic import BaseModel


VacancyArchiveReason = Literal[
    "Job filled",
    "Job closed or expired",
    "Employer removed the listing",
    "Duplicate vacancy",
    "Outside Scout's coverage or eligibility",
    "Other administrative reason",
]


class VacancyArchiveRequest(BaseModel):
    reason: VacancyArchiveReason
