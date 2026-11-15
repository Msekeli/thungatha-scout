from typing import Any
from urllib.parse import urlparse


_ATS_SUFFIXES = (
    ".greenhouse.io",
    ".lever.co",
    ".teamtailor.com",
    ".myworkdayjobs.com",
    ".workable.com",
)


def needs_targeted_logo_refresh(employer: dict[str, Any]) -> bool:
    if not employer.get("logo_url"):
        return True
    if employer.get("logo_type") == "official_ats_logo":
        return True
    for field in ("logo_url", "logo_source_url"):
        host = (urlparse(str(employer.get(field) or "")).hostname or "")
        host = host.casefold().rstrip(".")
        if any(host.endswith(suffix) for suffix in _ATS_SUFFIXES):
            return True
    return False
