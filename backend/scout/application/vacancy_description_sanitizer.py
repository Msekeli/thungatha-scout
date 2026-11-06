from html import escape, unescape
from html.parser import HTMLParser
from urllib.parse import urlparse

ALLOWED_TAGS = {
    "p",
    "br",
    "h1",
    "h2",
    "h3",
    "h4",
    "ul",
    "ol",
    "li",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "blockquote",
    "a",
}
VOID_TAGS = {"br"}
DROP_CONTENT = {"script", "style", "iframe", "object", "svg"}


class VacancyDescriptionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.output: list[str] = []
        self.open_tags: list[str] = []
        self.drop_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in DROP_CONTENT:
            self.drop_depth += 1
        if self.drop_depth or tag not in ALLOWED_TAGS:
            return
        attributes = ""
        if tag == "a":
            href = dict(attrs).get("href") or ""
            scheme = urlparse(href).scheme.lower()
            if scheme in {"http", "https", "mailto"}:
                attributes = f' href="{escape(href, quote=True)}"'
        self.output.append(f"<{tag}{attributes}>")
        if tag not in VOID_TAGS:
            self.open_tags.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in DROP_CONTENT and self.drop_depth:
            self.drop_depth -= 1
        if self.drop_depth or tag not in self.open_tags:
            return
        while self.open_tags:
            opened = self.open_tags.pop()
            self.output.append(f"</{opened}>")
            if opened == tag:
                break

    def handle_data(self, data: str) -> None:
        if not self.drop_depth:
            self.output.append(escape(data))

    def result(self) -> str:
        while self.open_tags:
            self.output.append(f"</{self.open_tags.pop()}>")
        return "".join(self.output).strip()


def sanitize_vacancy_description(value: str | None) -> str:
    if not value:
        return ""
    parser = VacancyDescriptionParser()
    parser.feed(unescape(value))
    parser.close()
    return parser.result()
