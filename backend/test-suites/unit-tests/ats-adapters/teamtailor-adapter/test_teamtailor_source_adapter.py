import asyncio

import httpx

from scout.ats_adapters.teamtailor_adapter.teamtailor_source_adapter import (
    TeamtailorSourceAdapter,
)

XML = """<rss xmlns:tt="https://teamtailor.com/locations"><channel>
<title>Root Platform</title><link>https://root.teamtailor.com/jobs</link>
<item><title>Junior Product Manager</title><description>&lt;p&gt;Support product&lt;/p&gt;</description>
<pubDate>Fri, 18 Sep 2026 14:25:54 +0200</pubDate>
<link>https://root.teamtailor.com/jobs/8403696-junior-product-manager</link>
<remoteStatus>hybrid</remoteStatus><guid>ae43e465-6807-4964-91b2-c8479023ae95</guid>
<tt:locations><tt:location><tt:name>Cape Town, South Africa</tt:name>
<tt:city>Cape Town</tt:city><tt:country>South Africa</tt:country></tt:location>
<tt:location><tt:name>Johannesburg, South Africa</tt:name><tt:city>Johannesburg</tt:city>
<tt:country>South Africa</tt:country></tt:location></tt:locations><tt:department>Product</tt:department><tt:role>Manager</tt:role>
</item></channel></rss>"""


def test_maps_teamtailor_vacancy_and_preserves_advert_link() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=XML)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await TeamtailorSourceAdapter(client).retrieve(
                {"careers_url": "https://root.teamtailor.com/jobs"}
            )

    result = asyncio.run(run())
    vacancy = result.vacancies[0]
    assert result.complete is True
    assert vacancy.external_job_id == "ae43e465-6807-4964-91b2-c8479023ae95"
    assert vacancy.location_text == "Cape Town, South Africa; Johannesburg, South Africa"
    assert vacancy.department == "Product"
    assert vacancy.description == "<p>Support product</p>"
    assert len(vacancy.raw_payload["locations"]) == 2
    assert vacancy.application_url.endswith("8403696-junior-product-manager")
    assert vacancy.published_at == "2026-09-18T12:25:54+00:00"
    assert vacancy.raw_payload["remoteStatus"] == "hybrid"
    assert vacancy.raw_payload["teamtailor_channel_title"] == "Root Platform"
