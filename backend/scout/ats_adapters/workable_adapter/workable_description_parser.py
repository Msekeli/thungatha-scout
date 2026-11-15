import re
from html.parser import HTMLParser


class WorkableDescriptionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str | None:
        value = "".join(self.parts).replace("\xa0", " ")
        lines = [re.sub(r"\s+", " ", part).strip() for part in value.splitlines()]
        result = "\n".join(part for part in lines if part)
        return result or None


def extract_workable_description(value: str | None) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parser = WorkableDescriptionParser()
    parser.feed(value)
    parser.close()
    return parser.text()
