import ipaddress
import json
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx

BLOCKED_LOGO_HOSTS = {
    "google.com",
    "www.google.com",
    "favicons.githubusercontent.com",
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
    "job-boards.eu.greenhouse.io",
    "jobs.lever.co",
    "jobs.eu.lever.co",
    "teamtailor.com",
}


def _blocked_logo_host(host: str) -> bool:
    normalized = host.casefold().rstrip(".")
    return (
        normalized in BLOCKED_LOGO_HOSTS
        or normalized in {"greenhouse.io", "lever.co"}
        or normalized.endswith((".teamtailor.com", ".greenhouse.io", ".lever.co"))
    )


def is_usable_employer_logo_url(value: str | None) -> bool:
    if not value:
        return False
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme in {"https", "http"}
            and bool(parsed.hostname)
            and not parsed.username
            and not parsed.password
            and not _blocked_logo_host(parsed.hostname)
        )
    except ValueError:
        return False


class BrandingMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.icons: list[str] = []
        self._json_ld = False
        self._json_text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "meta":
            key = values.get("property") or values.get("name") or values.get("itemprop")
            content = values.get("content")
            if key and content:
                self.meta[key.casefold()] = content.strip()
        if tag == "link":
            rel = set((values.get("rel") or "").casefold().split())
            href = values.get("href")
            if href and rel.intersection({"icon", "apple-touch-icon"}):
                self.icons.append(href)
        if (
            tag == "script"
            and (values.get("type") or "").casefold() == "application/ld+json"
        ):
            self._json_ld = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._json_ld = False

    def handle_data(self, data: str) -> None:
        if self._json_ld:
            self._json_text += data


def _structured_logo(value: object) -> str | None:
    if isinstance(value, list):
        for item in value:
            result = _structured_logo(item)
            if result:
                return result
    elif isinstance(value, dict):
        for key, item in value.items():
            if key.casefold() == "logo":
                if isinstance(item, str):
                    return item
                if isinstance(item, dict):
                    candidate = item.get("url") or item.get("contentUrl")
                    if isinstance(candidate, str):
                        return candidate
            result = _structured_logo(item)
            if result:
                return result
    return None


def _public_https_url(value: str, base_url: str) -> str | None:
    candidate = urljoin(base_url, value.strip())
    parsed = urlparse(candidate)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or _blocked_logo_host(parsed.hostname)
    ):
        return None
    return candidate


def _same_site_icon(value: str, page_url: str) -> str | None:
    candidate = _public_https_url(value, page_url)
    if not candidate:
        return None
    candidate_host = urlparse(candidate).hostname
    page_host = urlparse(page_url).hostname
    return (
        candidate
        if candidate_host and candidate_host.casefold() == (page_host or "").casefold()
        else None
    )


def _validate_public_host(url: str) -> None:
    host = urlparse(url).hostname
    if not host:
        raise ValueError("Branding URL has no hostname.")
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    if not addresses or any(
        not ipaddress.ip_address(item[4][0]).is_global for item in addresses
    ):
        raise ValueError("Branding URL must resolve to a public internet host.")


def extract_logo_asset(html: str, page_url: str) -> tuple[str, str] | None:
    parser = BrandingMetadataParser()
    parser.feed(html)

    structured = None
    if parser._json_text.strip():
        try:
            structured = _structured_logo(json.loads(parser._json_text))
        except (ValueError, TypeError):
            pass

    for candidate in (
        structured,
        parser.meta.get("og:logo"),
        parser.meta.get("logo"),
    ):
        if candidate:
            result = _public_https_url(candidate, page_url)
            if result:
                return result, "official_logo"

    for icon in parser.icons:
        result = _same_site_icon(icon, page_url)
        if result:
            return result, "official_favicon"
    return None


def extract_logo_url(html: str, page_url: str) -> str | None:
    asset = extract_logo_asset(html, page_url)
    return asset[0] if asset else None


async def discover_employer_logo(
    careers_url: str | None,
    website_url: str | None = None,
) -> tuple[str, str, str] | None:
    # Prefer the employer's own website. A careers URL is a safe fallback only
    # when it uses an employer-owned host, never a shared ATS host.
    candidates = []
    for value in (website_url, careers_url):
        if not value:
            continue
        parsed = urlparse(value)
        host = parsed.hostname or ""
        if parsed.scheme != "https" or _blocked_logo_host(host):
            continue
        if value not in candidates:
            candidates.append(value)

    if not candidates:
        return None

    try:
        async with httpx.AsyncClient(
            timeout=12,
            follow_redirects=True,
            headers={"User-Agent": "ThungathaScout/1.0 (+employer branding discovery)"},
        ) as client:
            for page_url in candidates:
                try:
                    _validate_public_host(page_url)
                    response = await client.get(page_url)
                    response.raise_for_status()
                    if "text/html" not in response.headers.get("content-type", "").casefold():
                        continue
                    source_url = str(response.url)
                    original_host = (
                        (urlparse(page_url).hostname or "").casefold().removeprefix("www.")
                    )
                    final_host = (
                        (urlparse(source_url).hostname or "").casefold().removeprefix("www.")
                    )
                    if _blocked_logo_host(final_host) or final_host != original_host:
                        continue
                    asset = extract_logo_asset(response.text, source_url)
                    if asset:
                        asset_url, asset_type = asset
                        return asset_url, source_url, asset_type

                    favicon_url = _same_site_icon("/favicon.ico", source_url)
                    if not favicon_url:
                        continue
                    favicon_response = await client.get(favicon_url)
                    favicon_response.raise_for_status()
                    if (
                        favicon_response.headers.get("content-type", "")
                        .casefold()
                        .startswith("image/")
                    ):
                        return favicon_url, source_url, "official_favicon"
                except (httpx.HTTPError, OSError, ValueError):
                    continue
    except (httpx.HTTPError, OSError, ValueError):
        return None
    return None
