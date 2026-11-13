import re
from html.parser import HTMLParser


class BrandingMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, list[str]] = {}
        self.icons: list[str] = []
        self.json_scripts: list[str] = []
        self.image_candidates: list[tuple[str, str]] = []
        self.branding_pages: list[str] = []
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
        if tag in {"img", "source"}:
            self._collect_image(values, tag)
        style = values.get("style") or ""
        hint = " ".join((values.get("class") or "", values.get("id") or ""))
        if style and any(token in hint.casefold() for token in ("logo", "brand")):
            for image in re.findall(r"background(?:-image)?\\s*:[^;]*url\\(['\\"]?([^)'\\"]+)", style):
                self.image_candidates.append((image, hint.casefold() + " background"))
        if tag == "a":
            href = values.get("href")
            label = " ".join(
                (values.get("aria-label") or "", values.get("title") or "")
            )
            if href and any(
                word in (href + " " + label).casefold()
                for word in ("about", "company", "who-we-are")
            ):
                self.branding_pages.append(href)
        if tag == "script" and (
            (values.get("type") or "").casefold() == "application/ld+json"
        ):
            self.json_scripts.append("")
            self._active_script = len(self.json_scripts) - 1

    def _collect_image(self, values: dict[str, str | None], tag: str) -> None:
        keys = ("src", "data-src", "data-lazy-src", "data-original")
        sources = [values.get(key) for key in keys]
        srcset = values.get("srcset") or values.get("data-srcset")
        if srcset:
            sources.extend(
                item.strip().split()[0] for item in srcset.split(",") if item.strip()
            )
        hint = " ".join(
            str(values.get(key) or "")
            for key in ("alt", "title", "class", "id", "itemprop", "aria-label")
        )
        if tag == "source":
            hint += " picture-source"
        for source in sources:
            if source:
                self.image_candidates.append((source.strip(), hint.casefold()))

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._active_script = None

    def handle_data(self, data: str) -> None:
        if self._active_script is not None:
            self.json_scripts[self._active_script] += data
