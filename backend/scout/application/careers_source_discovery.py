import ipaddress
import socket
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

import httpx

from scout.ats_adapters.greenhouse_adapter.greenhouse_career_site_discovery import (
    discover_greenhouse,
)
from scout.ats_adapters.greenhouse_adapter.greenhouse_contracts import parse_board_token
from scout.ats_adapters.lever_adapter.lever_url_parser import parse_lever_board_url

LEVER_HOSTS = {"jobs.lever.co", "jobs.eu.lever.co"}
GREENHOUSE_HOSTS = {
    "boards.greenhouse.io", "job-boards.greenhouse.io",
    "job-boards.eu.greenhouse.io",
}


class _CareersLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        key = "href" if tag == "a" else "src"
        if tag in {"a", "iframe", "script"} and values.get(key):
            self.links.append(values[key] or "")


def _validate_public_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username:
        raise ValueError("Enter a public HTTPS careers or ATS URL.")
    if parsed.password or parsed.port not in (None, 443):
        raise ValueError("Careers URLs cannot contain credentials or custom ports.")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    except OSError as exception:
        raise ValueError("Careers page host could not be resolved.") from exception
    if not addresses or any(
        not ipaddress.ip_address(item[4][0]).is_global for item in addresses
    ):
        raise ValueError("Careers page must resolve to a public internet host.")
    return value


async def _fetch_page(client: httpx.AsyncClient, value: str) -> tuple[str, str]:
    current = value
    for _ in range(4):
        _validate_public_url(current)
        response = await client.get(current, follow_redirects=False)
        if response.is_redirect:
            target = response.headers.get("location")
            if not target:
                raise ValueError("Careers page returned an invalid redirect.")
            current = urljoin(current, target)
            continue
        response.raise_for_status()
        return str(response.url), response.text
    raise ValueError("Careers page exceeded the redirect limit.")


async def discover_careers_source(url: str, company_name: str = "") -> dict:
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    if host in LEVER_HOSTS:
        from scout.api.lever_routes import inspect_lever_board
        result = await inspect_lever_board(url, company_name)
    elif host in GREENHOUSE_HOSTS:
        result = await discover_greenhouse(url, company_name)
        result.update({"outcome": "success", "complete": True, "jobs": []})
    else:
        origin = f"{parsed.scheme}://{parsed.netloc}"
        queue = deque([(url, 0)])
        visited: set[str] = set()
        candidates: dict[tuple[str, str], str] = {}
        async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
            while queue and len(visited) < 12:
                page_url, depth = queue.popleft()
                if page_url in visited:
                    continue
                visited.add(page_url)
                final_url, html = await _fetch_page(client, page_url)
                parser = _CareersLinks()
                parser.feed(html)
                for href in parser.links:
                    target = urljoin(final_url, href)
                    target_host = urlsplit(target).hostname or ""
                    if target_host in LEVER_HOSTS:
                        config, board_url = parse_lever_board_url(target)
                        candidates[("lever", board_url)] = target
                    elif target_host in GREENHOUSE_HOSTS:
                        token = parse_board_token(target)
                        candidates[("greenhouse", token)] = target
                    elif depth < 2 and target.startswith(origin):
                        queue.append((target, depth + 1))
        if len(candidates) != 1:
            raise ValueError(
                "Could not identify one unambiguous ATS board from this careers page. "
                "Paste the employer's direct ATS board URL."
            )
        (adapter, _), board_link = next(iter(candidates.items()))
        if adapter == "lever":
            from scout.api.lever_routes import inspect_lever_board
            result = await inspect_lever_board(board_link, company_name)
        else:
            result = await discover_greenhouse(board_link, company_name)
            result.update({"outcome": "success", "complete": True, "jobs": []})
    result["careers_url"] = url
    result["company_name"] = company_name or result.get("company_name", "")
    return result
