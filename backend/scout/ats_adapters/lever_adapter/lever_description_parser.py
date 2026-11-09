from html.parser import HTMLParser
import re


class LeverDescriptionParser(HTMLParser):
    BLOCK_TAGS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        value = "".join(self.parts).replace("\xa0", " ")
        lines = [re.sub(r"\s+", " ", line).strip() for line in value.splitlines()]
        return "\n".join(line for line in lines if line)


def extract_lever_description(plain: str | None, html: str | None) -> str | None:
    if isinstance(plain, str) and plain.strip():
        return plain.strip()
    if not isinstance(html, str) or not html.strip():
        return None
    parser = LeverDescriptionParser()
    parser.feed(html)
    parser.close()
    result = parser.text()
    return result or None
