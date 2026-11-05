import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urlparse, urlunparse

import httpx

HOSTS = {
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
    "job-boards.eu.greenhouse.io",
}
API_BOARD = re.compile(r"boards-api\.greenhouse\.io/v1/boards/([\w-]+)")


class CareersLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.in_title = self.in_script = False
        self.title_text = self.script_text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag in {"iframe", "script"} and values.get("src"):
            self.links.append(values["src"])
        self.in_title = self.in_title or tag == "title"
        self.in_script = self.in_script or tag == "script"

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "script":
            self.in_script = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_text += data
        if self.in_script:
            self.script_text += data


def _board_reference(parser: CareersLinks, page_url: httpx.URL) -> tuple[str, str] | None:
    for href in parser.links:
        link = page_url.join(href)
        if link.host not in HOSTS:
            continue
        parts = [part for part in link.path.split("/") if part]
        token = parts[0] if parts else ""
        if token == "jobs" and len(parts) > 1:
            token = parts[1]
        if token:
            return token, str(link.copy_with(path=f"/{token}", query="", fragment=""))
    script = parser.script_text.replace("\\/", "/")
    match = API_BOARD.search(script)
    if match:
        token = match.group(1)
        return token, f"https://job-boards.greenhouse.io/{token}"
    return None


async def discover_greenhouse(url: str) -> dict[str, str]:
    parsed = urlparse(url.strip())
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Enter a valid HTTPS careers or jobs URL.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not supported.")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    except OSError as exception:
        raise ValueError("Careers page host could not be resolved.") from exception
    if not addresses or any(
        not ipaddress.ip_address(item[4][0]).is_global for item in addresses
    ):
        raise ValueError("Careers page must resolve to a public internet host.")

    async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
        response = await client.get(url)
        response.raise_for_status()

    parser = CareersLinks()
    parser.feed(response.text)
    reference = _board_reference(parser, response.url)
    if reference:
        token, board_url = reference
        return {
            "careers_url": str(response.url),
            "board_url": board_url,
            "board_token": token,
            "detected_adapter": "greenhouse",
            "company_name": parser.title_text.split("|")[0].split("—")[0].strip(),
        }
    raise ValueError(
        "No Greenhouse board reference was found in links or embedded scripts."
    )
