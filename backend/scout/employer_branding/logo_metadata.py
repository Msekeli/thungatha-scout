import json
from urllib.parse import urljoin, urlparse

from scout.employer_branding.branding_metadata_parser import BrandingMetadataParser
from scout.employer_branding.logo_candidate_scoring import (
    conflicts_with_employer_name,
    score_logo_candidate,
)
from scout.employer_branding.logo_http import is_usable_employer_logo_url


def _logo_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [url for item in value for url in _logo_values(item)]
    if isinstance(value, dict):
        found = []
        for key, item in value.items():
            if key.casefold() == "logo":
                if isinstance(item, dict):
                    url = item.get("url") or item.get("contentUrl")
                    if isinstance(url, str):
                        found.append(url)
                    else:
                        found.extend(_logo_values(item))
                else:
                    found.extend(_logo_values(item))
            elif isinstance(item, (dict, list)):
                found.extend(_logo_values(item))
        return found
    return []


def extract_logo_assets(
    html: str, page_url: str, employer_name: str = ""
) -> list[tuple[str, str]]:
    parser = BrandingMetadataParser()
    parser.feed(html)
    page_host = (urlparse(page_url).hostname or "").casefold()
    lever_page = page_host in {"jobs.lever.co", "jobs.eu.lever.co"}
    ranked: list[tuple[int, str, str]] = []
    for script in parser.json_scripts:
        try:
            data = json.loads(script)
        except (ValueError, TypeError):
            continue
        ranked.extend(
            (score_logo_candidate(url, "", True), url, "official_logo")
            for url in _logo_values(data)
        )
    for key in ("og:logo", "logo"):
        ranked.extend(
            (score_logo_candidate(url, "", True), url, "official_logo")
            for url in parser.meta.get(key, [])
        )
    if lever_page:
        ranked.extend(
            (
                score_logo_candidate(url, "lever employer logo", True),
                url,
                "official_ats_logo",
            )
            for url in parser.meta.get("og:image", [])
        )
    for value, hint in parser.image_candidates:
        score = score_logo_candidate(value, hint)
        if score > 0:
            ranked.append((score, value, "official_logo"))
    page_host = page_host.removeprefix("www.")
    ranked_urls = []
    for score, value, logo_type in ranked:
        url = urljoin(page_url, value.strip())
        host = (urlparse(url).hostname or "").casefold().removeprefix("www.")
        if (
            score <= 0
            or not is_usable_employer_logo_url(url)
            or not host
            or conflicts_with_employer_name(url, employer_name)
        ):
            continue
        ranked_urls.append((score + (35 if host == page_host else 0), url, logo_type))
    result = []
    for _, url, logo_type in sorted(set(ranked_urls), reverse=True):
        result.append((url, logo_type))
    return result


def extract_logo_asset(html: str, page_url: str) -> tuple[str, str] | None:
    assets = extract_logo_assets(html, page_url)
    return assets[0] if assets else None


def extract_logo_url(html: str, page_url: str) -> str | None:
    return asset[0] if (asset := extract_logo_asset(html, page_url)) else None
