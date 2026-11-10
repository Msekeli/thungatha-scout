import httpx
from xml.etree import ElementTree

from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_contracts import (
    TeamtailorFeed,
    TeamtailorFeedResult,
)
from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_parser import (
    NotTeamtailorFeedError,
    parse_teamtailor_feed,
)


async def request_teamtailor_feed_page(
    client: httpx.AsyncClient,
    careers_url: str,
    feed_url: str,
    offset: int,
    page_size: int,
    previous_jobs: list[dict],
    channel_title: str | None,
) -> TeamtailorFeed | TeamtailorFeedResult:
    try:
        response = await client.get(
            feed_url,
            params={"offset": offset, "per_page": page_size},
        )
    except httpx.HTTPError:
        return _failure(
            previous_jobs, offset // page_size, "Teamtailor request failed.", "transient_failure", channel_title
        )
    if not response.is_success:
        outcome = {
            401: "blocked", 403: "blocked", 404: "not_found", 429: "rate_limited"
        }.get(response.status_code)
        outcome = outcome or (
            "transient_failure" if response.status_code >= 500 else "malformed"
        )
        return _failure(
            previous_jobs,
            offset // page_size,
            f"Teamtailor returned HTTP {response.status_code}.",
            outcome,
            channel_title,
        )
    try:
        feed = parse_teamtailor_feed(response.content, careers_url)
    except NotTeamtailorFeedError:
        raise
    except (ElementTree.ParseError, ValueError) as exception:
        return _failure(
            previous_jobs,
            offset // page_size,
            f"Invalid Teamtailor RSS: {exception}",
            "malformed",
            channel_title,
        )
    if channel_title and feed.channel_title and channel_title != feed.channel_title:
        return _failure(
            previous_jobs,
            offset // page_size + 1,
            "Teamtailor channel title changed during pagination.",
            "partial",
            channel_title,
        )
    return feed


def _failure(jobs, pages, detail, outcome, title):
    return TeamtailorFeedResult(
        "partial" if jobs else outcome, jobs, pages, False, detail, title
    )
