import ipaddress
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

import httpx


class CareersLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        key = "href" if tag == "a" else "src"
        if tag in {"a", "iframe", "script"} and values.get(key):
            self.links.append(values[key] or "")


def validate_public_url(value: str) -> None:
    parsed = urlsplit(value)
    try:
        port = parsed.port
    except ValueError as exception:
        raise ValueError("Careers URL contains an invalid port.") from exception
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or port not in (None, 443)
    ):
        raise ValueError("Enter a public HTTPS careers or ATS URL.")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    except OSError as exception:
        raise ValueError("Careers page host could not be resolved.") from exception
    if not addresses or any(
        not ipaddress.ip_address(item[4][0]).is_global for item in addresses
    ):
        raise ValueError("Careers page must resolve to a public internet host.")


async def read_careers_page(
    client: httpx.AsyncClient, value: str
) -> tuple[str, list[str]]:
    current = value
    for _ in range(4):
        validate_public_url(current)
        response = await client.get(current, follow_redirects=False)
        if response.is_redirect:
            target = response.headers.get("location")
            if not target:
                raise ValueError("Careers page returned an invalid redirect.")
            current = urljoin(current, target)
            continue
        response.raise_for_status()
        parser = CareersLinks()
        parser.feed(response.text)
        return str(response.url), parser.links
    raise ValueError("Careers page exceeded the redirect limit.")
