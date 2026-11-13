import re
from urllib.parse import urlparse

ATS_SUFFIXES = (".greenhouse.io", ".lever.co", ".teamtailor.com")


def careers_page_matches_employer(name: str, careers_url: str | None) -> bool:
    if not careers_url:
        return False
    parsed = urlparse(careers_url)
    host = (parsed.hostname or "").casefold().removeprefix("www.")
    compact_name = re.sub(r"[^a-z0-9]", "", name.casefold())
    if not host or not compact_name:
        return False
    if compact_name in re.sub(r"[^a-z0-9]", "", host):
        return True
    if host.endswith(ATS_SUFFIXES) or host.endswith(".myworkdayjobs.com"):
        parts = [part for part in parsed.path.split("/") if part]
        identifiers = [host.split(".")[0], parts[0] if parts else ""]
        return any(
            compact_name in re.sub(r"[^a-z0-9]", "", value.casefold())
            or re.sub(r"[^a-z0-9]", "", value.casefold()) in compact_name
            for value in identifiers if len(value) >= 4
        )
    return False
