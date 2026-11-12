import asyncio
import os

import pytest

from scout.ats_adapters.workday_adapter.workday_cxs_client import WorkdayCxsClient
from scout.ats_adapters.workday_adapter.workday_url_parser import (
    parse_workday_board_url,
)
from scout.ats_adapters.workday_adapter.workday_vacancy_mapper import (
    map_workday_vacancy,
)


LIVE_SOURCES = [
    "https://myhcm.wd3.myworkdayjobs.com/digioutsource",
    "https://oldmutual.wd3.myworkdayjobs.com/Old_Mutual_Careers",
]


@pytest.mark.skipif(
    os.getenv("WORKDAY_LIVE_TESTS") != "1",
    reason="Set WORKDAY_LIVE_TESTS=1 to call public Workday sites.",
)
@pytest.mark.parametrize("board_url", LIVE_SOURCES)
def test_public_workday_tenant_listing_and_detail(board_url: str) -> None:
    config, _ = parse_workday_board_url(board_url)
    host = f"{config['host_prefix']}.myworkdayjobs.com"

    async def run():
        client = WorkdayCxsClient()
        try:
            listing = await client.list_jobs(config)
            assert listing.complete is True, listing.detail
            assert listing.total > 0
            detail = await client.get_detail(
                config, listing.postings[0]["externalPath"]
            )
            assert detail.posting is not None, detail.detail
            vacancy = map_workday_vacancy(
                listing.postings[0], detail.posting, host, config["site"]
            )
            assert vacancy.description
            assert vacancy.application_url.startswith("https://")
            assert vacancy.external_job_id
            return listing.total, vacancy
        finally:
            await client.close()

    total, vacancy = asyncio.run(run())
    assert total > 0
    assert vacancy.title
