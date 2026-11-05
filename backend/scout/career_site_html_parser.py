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


def find_greenhouse_board_reference(
    parser: CareersLinks, page_url: httpx.URL
) -> tuple[str, str] | None:
    for href in parser.links:
        link = page_url.join(href)
        if link.host not in HOSTS:
            continue
        parts = [part for part in link.path.split("/") if part]
        token = parts[0] if parts else ""
        if token == "jobs" and len(parts) > 1:
            token = parts[1]
        if token:
            board = link.copy_with(path=f"/{token}", query="", fragment="")
            return token, str(board)
    match = API_BOARD.search(parser.script_text.replace("\\/", "/"))
    if match:
        token = match.group(1)
        return token, f"https://job-boards.greenhouse.io/{token}"
    return None
