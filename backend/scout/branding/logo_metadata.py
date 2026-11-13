import json
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

from scout.branding.logo_http import is_usable_employer_logo_url


class BrandingMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, list[str]] = {}
        self.icons: list[str] = []
        self.json_scripts: list[str] = []
        self._active_script: int | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "meta":
            key = values.get("property") or values.get("name") or values.get("itemprop")
            content = values.get("content")
            if key and content:
                self.meta.setdefault(key.casefold(), []).append(content.strip())
        if tag == "link":
            rel = set((values.get("rel") or "").casefold().split())
            href = values.get("href")
            if href and rel.intersection({"icon", "apple-touch-icon"}):
                self.icons.append(href)
        if tag == "script" and (values.get("type") or "").casefold() == "application/ld+json":
            self.json_scripts.append("")
            self._active_script = len(self.json_scripts) - 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._active_script = None

    def handle_data(self, data: str) -> None:
        if self._active_script is not None:
            self.json_scripts[self._active_script] += data


def _structured_logo(value: object) -> str | None:
    if isinstance(value, list):
        return next((found for item in value if (found := _structured_logo(item))), None)
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
        candidates.extend((value, "official_logo") for value in parser.meta.get(key, []))
    page_host = (urlparse(page_url).hostname or "").casefold()
    candidates.extend((icon, "official_favicon") for icon in parser.icons)
    result: list[tuple[str, str]] = []
    for value, kind in candidates:
        url = urljoin(page_url, value.strip())
        if not is_usable_employer_logo_url(url) or url in {item[0] for item in result}:
            continue
        if kind == "official_favicon" and (urlparse(url).hostname or "").casefold() != page_host:
            continue
        result.append((url, kind))
    return result


def extract_logo_asset(html: str, page_url: str) -> tuple[str, str] | None:
    assets = extract_logo_assets(html, page_url)
    return assets[0] if assets else None


def extract_logo_url(html: str, page_url: str) -> str | None:
    asset = extract_logo_asset(html, page_url)
    return asset[0] if asset else None
