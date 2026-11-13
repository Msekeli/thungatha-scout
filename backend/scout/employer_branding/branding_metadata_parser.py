from html.parser import HTMLParser


class BrandingMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, list[str]] = {}
        self.icons: list[str] = []
        self.json_scripts: list[str] = []
        self._active_script: int | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "meta":
            key = values.get("property") or values.get("name") or values.get("itemprop")
            content = values.get("content")
            if key and content:
                self.meta.setdefault(key.casefold(), []).append(content.strip())
        if tag == "link":
            rel = set((values.get("rel") or "").casefold().split())
            href = values.get("href")
            if href and rel.intersection({"icon", "apple-touch-icon"}):
                self.icons.append(href)
        if (
            tag == "script"
            and (values.get("type") or "").casefold() == "application/ld+json"
        ):
            self.json_scripts.append("")
            self._active_script = len(self.json_scripts) - 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._active_script = None

    def handle_data(self, data: str) -> None:
        if self._active_script is not None:
            self.json_scripts[self._active_script] += data
