import json
from urllib.parse import urljoin, urlparse

from scout.ats_adapters.ats_adapter_contracts import NormalizedVacancy


_ATS_HOSTS = {
    "greenhouse": ("greenhouse.io",),
    "lever": ("lever.co",),
    "workday": ("myworkdayjobs.com",),
    "workable": ("workable.com",),
    "teamtailor": ("teamtailor.com",),
}


def fingerprint_platform(url: str) -> str | None:
    host = (urlparse(url).hostname or "").lower()
    for adapter, domains in _ATS_HOSTS.items():
        if any(host == domain or host.endswith(f".{domain}") for domain in domains):
            return adapter
    return None


def _job_types(value: object) -> bool:
    types = value if isinstance(value, list) else [value]
    return any(str(item).rsplit("/", 1)[-1] == "JobPosting" for item in types)


def parse_job_postings(
    scripts: list[str], source_url: str
) -> list[NormalizedVacancy]:
    vacancies: list[NormalizedVacancy] = []
    for script in scripts:
        try:
            payload = json.loads(script)
        except (TypeError, ValueError):
            continue
        candidates = payload if isinstance(payload, list) else [payload]
        for candidate in candidates:
            if isinstance(candidate, dict) and "@graph" in candidate:
                graph = candidate["@graph"]
                candidates.extend(graph if isinstance(graph, list) else [])
                continue
            if not isinstance(candidate, dict) or not _job_types(candidate.get("@type")):
                continue
            vacancy = _map_job_posting(candidate, source_url)
            if vacancy:
                vacancies.append(vacancy)
    return vacancies


def _map_job_posting(
    item: dict, source_url: str
) -> NormalizedVacancy | None:
    title = item.get("title")
    url = urljoin(source_url, str(item.get("url") or source_url))
    if not isinstance(title, str) or not title.strip():
        return None
    identifier = item.get("identifier")
    external_id = identifier.get("value") if isinstance(identifier, dict) else identifier
    description = item.get("description")
    return NormalizedVacancy(
        external_job_id=str(external_id or url),
        title=title.strip(),
        description=description if isinstance(description, str) else None,
        location_text=_job_location(item.get("jobLocation")),
        department=None,
        office=None,
        application_url=url,
        published_at=item.get("datePosted"),
        source_updated_at=item.get("dateModified"),
        raw_payload=item,
    )


def _job_location(location: object) -> str | None:
    if isinstance(location, list):
        location = location[0] if location else None
    address = location.get("address") if isinstance(location, dict) else None
    if not isinstance(address, dict):
        return None
    parts = (address.get("addressLocality"), address.get("addressRegion"))
    value = ", ".join(str(part) for part in parts if part)
    return value or None
