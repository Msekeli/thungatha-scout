import json
from urllib.parse import urljoin, urlparse

from scout.employer_branding.branding_metadata_parser import BrandingMetadataParser
from scout.employer_branding.logo_http import is_usable_employer_logo_url


_EXCLUDED_HINTS = ("favicon", "apple-touch", "avatar", "social", "share", "banner")
_LOGO_HINTS = ("logo", "brandmark", "brand-mark", "wordmark", "brand mark")


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
            else:
                found.extend(_logo_values(item))
        return found
    return []


def _score(value: str, hint: str, explicit: bool = False) -> int:
    text = (value + " " + hint).casefold()
    if any(token in text for token in _EXCLUDED_HINTS):
        return -100
    score = 100 if explicit else 0
    if any(token in text for token in _LOGO_HINTS):
        score += 80
    if any(token in value.casefold() for token in ("logo", "wordmark", "brandmark")):
        score += 45
    if "header" in hint or "navbar" in hint or "navigation" in hint:
        score += 20
    if any(token in value.casefold() for token in ("og-image", "opengraph", "cover")):
        score -= 70
    return score


def extract_logo_assets(html: str, page_url: str) -> list[tuple[str, str]]:
    parser = BrandingMetadataParser()
    parser.feed(html)
    ranked: list[tuple[int, str]] = []
    for script in parser.json_scripts:
        try:
            data = json.loads(script)
        except (ValueError, TypeError):
            continue
        ranked.extend((_score(url, "", True), url) for url in _logo_values(data))
    for key in ("og:logo", "logo"):
        ranked.extend((_score(url, "", True), url) for url in parser.meta.get(key, []))
    for value, hint in parser.image_candidates:
        score = _score(value, hint)
        if score > 0:
            ranked.append((score, value))
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for score, value in sorted(ranked, reverse=True):
        url = urljoin(page_url, value.strip())
        if (score <= 0 or url in seen or not is_usable_employer_logo_url(url)
                or not urlparse(url).hostname):
            continue
        seen.add(url)
        result.append((url, "official_logo"))
    return result


def extract_logo_asset(html: str, page_url: str) -> tuple[str, str] | None:
    assets = extract_logo_assets(html, page_url)
    return assets[0] if assets else None


def extract_logo_url(html: str, page_url: str) -> str | None:
    asset = extract_logo_asset(html, page_url)
    return asset[0] if asset else None
