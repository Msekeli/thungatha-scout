import ipaddress
import json
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx


class BrandingMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.image_src: str | None = None
        self._json_ld = False
        self._json_text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "meta":
            key = values.get("property") or values.get("name") or values.get("itemprop")
            content = values.get("content")
            if key and content:
                self.meta[key.casefold()] = content.strip()
        if tag == "link" and "image_src" in (values.get("rel") or "").casefold():
            self.image_src = values.get("href")
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
    ):
        return None
    return candidate


def _validate_public_host(url: str) -> None:
    host = urlparse(url).hostname
    if not host:
        raise ValueError("Branding URL has no hostname.")
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    if not addresses or any(
        not ipaddress.ip_address(item[4][0]).is_global for item in addresses
    ):
        raise ValueError("Branding URL must resolve to a public internet host.")


def extract_logo_url(html: str, page_url: str) -> str | None:
    parser = BrandingMetadataParser()
    parser.feed(html)

    structured = None
    if parser._json_text.strip():
        try:
            structured = _structured_logo(json.loads(parser._json_text))
        except (ValueError, TypeError):
            pass

    candidates = [
        structured,
        parser.meta.get("og:logo"),
        parser.meta.get("logo"),
        parser.meta.get("twitter:image"),
        parser.meta.get("twitter:image:src"),
        parser.meta.get("og:image"),
        parser.image_src,
    ]
    for candidate in candidates:
        if candidate:
            result = _public_https_url(candidate, page_url)
            if result:
                return result
    return None


async def discover_employer_logo(
    careers_url: str,
    website_url: str | None = None,
) -> tuple[str, str] | None:
    for page_url in (website_url, careers_url):
        if not page_url:
            continue
        try:
            _validate_public_host(page_url)
            async with httpx.AsyncClient(
                timeout=12,
                follow_redirects=False,
                headers={
                    "User-Agent": "ThungathaScout/1.0 (+employer branding discovery)"
                },
            ) as client:
                response = await client.get(page_url)
                response.raise_for_status()
                if (
                    "text/html"
                    not in response.headers.get("content-type", "").casefold()
                ):
                    continue
                logo_url = extract_logo_url(response.text, str(response.url))
                if logo_url:
                    return logo_url, str(response.url)
        except (httpx.HTTPError, OSError, ValueError):
            continue
    return None
