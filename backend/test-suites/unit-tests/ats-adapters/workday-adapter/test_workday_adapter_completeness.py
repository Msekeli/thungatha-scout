import asyncio

from scout.ats_adapters.workday_adapter.workday_contracts import (
    WorkdayDetailResult,
    WorkdayListResult,
)
from scout.ats_adapters.workday_adapter.workday_source_adapter import (
    WorkdaySourceAdapter,
)


class FakeWorkdayClient:
    def __init__(self, postings, detail):
        self.postings = postings
        self.detail = detail

    async def list_jobs(self, config):
        return WorkdayListResult("success", self.postings, len(self.postings), 1, True)

    async def get_detail(self, config, path):
        return WorkdayDetailResult("success", self.detail)

    async def close(self):
        return None


def test_duplicate_requisition_ids_make_inventory_partial() -> None:
    postings = [
        {"title": "Developer", "externalPath": "/job/One", "bulletFields": ["JR1"]},
        {"title": "Developer", "externalPath": "/job/Two", "bulletFields": ["JR1"]},
    ]
    detail = {"jobPostingInfo": {
        "jobReqId": "JR1", "title": "Developer", "jobDescription": "<p>Build</p>"
    }}

    result = asyncio.run(WorkdaySourceAdapter(
        FakeWorkdayClient(postings, detail)
    ).retrieve({"host_prefix": "oldmutual.wd3", "site": "Old_Mutual_Careers"}))

    assert result.outcome == "partial"
    assert result.complete is False
    assert len(result.vacancies) == 1


def test_missing_description_makes_inventory_partial() -> None:
    posting = {"title": "Developer", "externalPath": "/job/One"}
    detail = {"jobPostingInfo": {"jobReqId": "JR1", "title": "Developer"}}

    result = asyncio.run(WorkdaySourceAdapter(
        FakeWorkdayClient([posting], detail)
    ).retrieve({"host_prefix": "oldmutual.wd3", "site": "Old_Mutual_Careers"}))

    assert result.outcome == "partial"
    assert result.complete is False
    assert result.vacancies == []


def test_fallback_job_url_preserves_source_locale() -> None:
    posting = {"title": "Developer", "externalPath": "/job/Cape-Town/Dev_JR1"}
    detail = {"jobPostingInfo": {
        "jobReqId": "JR1", "title": "Developer", "jobDescription": "<p>Build</p>"
    }}

    result = asyncio.run(WorkdaySourceAdapter(
        FakeWorkdayClient([posting], detail)
    ).retrieve({
        "host_prefix": "oldmutual.wd3", "site": "Old_Mutual_Careers",
        "tenant": "oldmutual", "locale": "fr-FR",
    }))

    assert result.vacancies[0].application_url.endswith(
        "/fr-FR/Old_Mutual_Careers/job/Cape-Town/Dev_JR1"
    )
