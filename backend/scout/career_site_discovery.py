from html.parser import HTMLParser
from urllib.parse import urlparse, urlunparse

import httpx

HOSTS = {
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
    "job-boards.eu.greenhouse.io",
}


class CareersLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        href = dict(attrs).get("href")
        if tag == "a" and href:
            self.links.append(href)


async def discover_greenhouse(url: str) -> dict[str, str]:
    parsed = urlparse(url.strip())
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Enter a valid HTTPS careers or jobs URL.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not supported.")

    async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
        response = await client.get(url)
        response.raise_for_status()

    parser = CareersLinks()
    parser.feed(response.text)
    for href in parser.links:
        link = response.url.join(href)
        if link.host not in HOSTS:
            continue
        parts = [part for part in link.path.split("/") if part]
        token = parts[0] if parts else ""
        if token == "jobs" and len(parts) > 1:
            token = parts[1]
        if token:
            board_url = urlunparse(
                (link.scheme, link.netloc, f"/{token}", "", "", "")
            )
            return {
                "careers_url": str(response.url),
                "board_url": board_url,
                "board_token": token,
                "detected_adapter": "greenhouse",
            }
    raise ValueError(
        "No Greenhouse board link was found. "
        "This careers page may load its jobs dynamically."
    )
