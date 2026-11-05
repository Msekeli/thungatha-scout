import re
from html.parser import HTMLParser

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


def _board_token(link: httpx.URL) -> str | None:
    parts = [part for part in link.path.split("/") if part]
    if link.path.startswith("/embed/"):
        return link.params.get("for")
    return parts[0] if parts and parts[0] != "jobs" else None


def find_greenhouse_board_candidates(
    parser: CareersLinks, page_url: httpx.URL
) -> list[str]:
    candidates: list[str] = []
    if page_url.host in HOSTS:
        token = _board_token(page_url)
        if token:
            candidates.append(token)
    for href in parser.links:
        link = page_url.join(href)
        if link.host not in HOSTS:
            continue
        token = _board_token(link)
        if token and token not in candidates:
            candidates.append(token)
    scripts = parser.script_text.replace("\\/", "/")
    for match in API_BOARD.finditer(scripts):
        if match.group(1) not in candidates:
            candidates.append(match.group(1))
    return candidates
