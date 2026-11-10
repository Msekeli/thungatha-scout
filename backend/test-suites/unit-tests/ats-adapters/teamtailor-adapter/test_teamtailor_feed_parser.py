import pytest

from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_parser import (
    NotTeamtailorFeedError,
    parse_teamtailor_feed,
)

XML = b"""<?xml version="1.0"?>
<rss version="2.0" xmlns:tt="https://teamtailor.com/locations">
<channel><title>Root Platform</title><link>https://root.teamtailor.com/jobs</link>
<item><title>Engineer</title><description>&lt;p&gt;Build software&lt;/p&gt;</description>
<pubDate>Fri, 18 Sep 2026 14:25:54 +0200</pubDate>
<link>https://root.teamtailor.com/jobs/123-engineer</link>
<remoteStatus>hybrid</remoteStatus><guid>global-id-1</guid>
<tt:locations><tt:location><tt:name>Cape Town</tt:name>
<tt:city>Cape Town</tt:city><tt:country>South Africa</tt:country>
</tt:location></tt:locations><tt:department>Engineering</tt:department>
<tt:role>Developer</tt:role><tt:division>Platform</tt:division></item>
</channel></rss>"""


def test_parses_documented_fields_and_teamtailor_namespace() -> None:
    feed = parse_teamtailor_feed(XML, "https://root.teamtailor.com/jobs")
    job = feed.jobs[0]
    assert feed.channel_title == "Root Platform"
    assert job["guid"] == "global-id-1"
    assert job["remoteStatus"] == "hybrid"
    assert job["department"] == "Engineering"
    assert job["role"] == "Developer"
    assert job["division"] == "Platform"
    assert job["locations"][0]["country"] == "South Africa"


def test_rejects_non_teamtailor_feed_and_wrong_custom_domain() -> None:
    with pytest.raises(NotTeamtailorFeedError):
        parse_teamtailor_feed(b"<rss><channel /></rss>", "https://root.teamtailor.com/jobs")
    with pytest.raises(NotTeamtailorFeedError):
        parse_teamtailor_feed(XML, "https://other.example/jobs")
