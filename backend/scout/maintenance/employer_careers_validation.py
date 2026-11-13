import re
from urllib.parse import urlparse

ATS_SUFFIXES = (
    ".greenhouse.io", ".lever.co", ".teamtailor.com",
    ".myworkdayjobs.com", ".workable.com",
)


def careers_page_matches_employer(
    name: str, careers_url: str | None, website_url: str | None = None
) -> bool:
    if not careers_url:
        return False
    parsed = urlparse(careers_url)
    host = (parsed.hostname or "").casefold().removeprefix("www.")
    compact_name = re.sub(r"[^a-z0-9]", "", name.casefold())
    if not host or not compact_name:
        return False
    if website_url:
        website_host = (urlparse(website_url).hostname or "").casefold()
        website_host = website_host.removeprefix("www.")
        if host == website_host or host.endswith("." + website_host):
            return True
    if compact_name in re.sub(r"[^a-z0-9]", "", host):
        return True
    if host.endswith(ATS_SUFFIXES):
        parts = [part for part in parsed.path.split("/") if part]
        identifiers = [host.split(".")[0], *parts[:2]]
        return any(
            compact_name in re.sub(r"[^a-z0-9]", "", value.casefold())
            or re.sub(r"[^a-z0-9]", "", value.casefold()) in compact_name
            for value in identifiers if len(value) >= 2
        )
    return False
