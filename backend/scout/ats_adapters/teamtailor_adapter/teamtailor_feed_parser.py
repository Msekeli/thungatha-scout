from urllib.parse import urlsplit
from xml.etree import ElementTree

from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_contracts import (
    TeamtailorFeed,
)

TEAMTAILOR_NAMESPACE = "https://teamtailor.com/locations"


class NotTeamtailorFeedError(ValueError):
    pass


def parse_teamtailor_feed(content: bytes, careers_url: str) -> TeamtailorFeed:
    if TEAMTAILOR_NAMESPACE.encode() not in content:
        raise NotTeamtailorFeedError("Response is not a Teamtailor RSS feed.")
    root = ElementTree.fromstring(content)
    if root.tag != "rss":
        raise NotTeamtailorFeedError("Response is not a Teamtailor RSS feed.")
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Teamtailor RSS channel is missing.")
    _validate_channel_link(channel.findtext("link"), careers_url)
    jobs = [_parse_item(item) for item in channel.findall("item")]
    return TeamtailorFeed(channel.findtext("title"), jobs)


def _validate_channel_link(value: str | None, careers_url: str) -> None:
    if not value:
        raise ValueError("Teamtailor RSS channel link is missing.")
    actual, expected = urlsplit(value), urlsplit(careers_url)
    if actual.hostname != expected.hostname:
        raise NotTeamtailorFeedError("RSS feed belongs to a different careers site.")
    if actual.path.rstrip("/") != expected.path.rstrip("/"):
        raise NotTeamtailorFeedError("RSS feed does not match the supplied careers URL.")


def _parse_item(item: ElementTree.Element) -> dict:
    fields = ("title", "description", "pubDate", "link", "remoteStatus", "guid")
    job = {field: item.findtext(field) for field in fields}
    for field in ("company_name", "company_uuid"):
        job[field] = item.findtext(field)
    namespace = f"{{{TEAMTAILOR_NAMESPACE}}}"
    locations = item.find(f"{namespace}locations")
    job["locations"] = (
        [_location(node, namespace) for node in locations.findall(f"{namespace}location")]
        if locations is not None
        else []
    )
    for field in ("department", "role", "division"):
        job[field] = item.findtext(f"{namespace}{field}")
    return job


def _location(node: ElementTree.Element, namespace: str) -> dict[str, str | None]:
    return {
        field: node.findtext(f"{namespace}{field}")
        for field in ("name", "address", "zip", "city", "country")
    }
