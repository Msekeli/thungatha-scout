import json
from urllib.parse import urljoin, urlparse

from scout.branding.branding_metadata_parser import BrandingMetadataParser
from scout.branding.logo_http import is_usable_employer_logo_url


def _structured_logo(value: object) -> str | None:
    if isinstance(value, list):
        return next(
            (found for item in value if (found := _structured_logo(item))), None
        )
    if isinstance(value, dict):
        for key, item in value.items():
            if key.casefold() == "logo":
                if isinstance(item, str):
                    return item
                if isinstance(item, dict):
                    candidate = item.get("url") or item.get("contentUrl")
                    if isinstance(candidate, str):
                        return candidate
            found = _structured_logo(item)
            if found:
                return found
    return None


def extract_logo_assets(html: str, page_url: str) -> list[tuple[str, str]]:
    parser = BrandingMetadataParser()
    parser.feed(html)
    candidates: list[tuple[str, str]] = []
    for script in parser.json_scripts:
        try:
            logo = _structured_logo(json.loads(script))
        except (ValueError, TypeError):
            logo = None
        if logo:
            candidates.append((logo, "official_logo"))
    for key in ("og:logo", "logo"):
        candidates.extend(
            (value, "official_logo") for value in parser.meta.get(key, [])
        )
    page_host = (urlparse(page_url).hostname or "").casefold()
    candidates.extend((icon, "official_favicon") for icon in parser.icons)
    result: list[tuple[str, str]] = []
    for value, kind in candidates:
        url = urljoin(page_url, value.strip())
        if not is_usable_employer_logo_url(url) or url in {item[0] for item in result}:
            continue
        if (
            kind == "official_favicon"
            and (urlparse(url).hostname or "").casefold() != page_host
        ):
            continue
        result.append((url, kind))
    return result


def extract_logo_asset(html: str, page_url: str) -> tuple[str, str] | None:
    assets = extract_logo_assets(html, page_url)
    return assets[0] if assets else None


def extract_logo_url(html: str, page_url: str) -> str | None:
    asset = extract_logo_asset(html, page_url)
    return asset[0] if asset else None
