import json
import re
from urllib.parse import urljoin, urlparse
from scout.employer_branding.branding_metadata_parser import BrandingMetadataParser
from scout.employer_branding.logo_http import is_usable_employer_logo_url
_EXCLUDED = ("favicon", "apple-touch", "avatar", "social", "share", "banner")
_HINTS = ("logo", "brandmark", "brand-mark", "wordmark", "brand mark")
def _logo_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [url for item in value for url in _logo_values(item)]
    if isinstance(value, dict):
        found = []
        for key, item in value.items():
            if key.casefold() == "logo":
                if isinstance(item, dict):
                    url = item.get("url") or item.get("contentUrl")
                    if isinstance(url, str):
                        found.append(url)
                    else:
                        found.extend(_logo_values(item))
                else:
                    found.extend(_logo_values(item))
            elif isinstance(item, (dict, list)):
                found.extend(_logo_values(item))
        return found
    return []
def _tokens(value: str) -> set[str]:
    return {part.casefold() for part in re.findall(r"[a-zA-Z0-9]+", value)}
def _conflicting_brand_name(url: str, employer_name: str) -> bool:
    path = urlparse(url).path.rsplit("/", 1)[-1].casefold()
    words = _tokens(re.sub(r"\.[a-z0-9]+$", "", path))
    ignored = {"logo", "brand", "mark", "word", "white", "dark"}
    employer_words = _tokens(employer_name)
    brand_words = {
        word for word in words - ignored
        if (word.isalpha() and len(word) >= 3) or word in employer_words
    }
    overlap = any(
        a == b or a.startswith(b) or b.startswith(a)
        for a in brand_words for b in employer_words
    )
    return bool(employer_name.strip()) and bool(brand_words) and not overlap
def _score(value: str, hint: str, explicit: bool = False) -> int:
    text = (value + " " + hint).casefold()
    if any(token in text for token in _EXCLUDED):
        return -100
    score = 100 if explicit else 0
    if any(token in text for token in _HINTS):
        score += 80
    if any(token in value.casefold() for token in ("logo", "wordmark", "brandmark")):
        score += 35
    if any(token in hint for token in ("header", "navbar", "navigation")):
        score += 20
    if any(token in value.casefold() for token in ("og-image", "opengraph", "cover")):
        score -= 70
    return score
def extract_logo_assets(
    html: str, page_url: str, employer_name: str = ""
) -> list[tuple[str, str]]:
    parser = BrandingMetadataParser()
    parser.feed(html)
    ranked: list[tuple[int, str]] = []
    for script in parser.json_scripts:
        try:
            data = json.loads(script)
        except (ValueError, TypeError):
            continue
        ranked.extend((_score(url, "", True), url) for url in _logo_values(data))
    for key in ("og:logo", "logo"):
        ranked.extend((_score(url, "", True), url) for url in parser.meta.get(key, []))
    for value, hint in parser.image_candidates:
        score = _score(value, hint)
        if score > 0:
            ranked.append((score, value))
    page_host = (urlparse(page_url).hostname or "").casefold().removeprefix("www.")
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    ranked_urls = []
    for score, value in ranked:
        url = urljoin(page_url, value.strip())
        host = (urlparse(url).hostname or "").casefold().removeprefix("www.")
        if (
            score <= 0 or not is_usable_employer_logo_url(url) or not host
            or _conflicting_brand_name(url, employer_name)
        ):
            continue
        ranked_urls.append((score + (35 if host == page_host else 0), url))
    for _, url in sorted(ranked_urls, reverse=True):
        if url in seen:
            continue
        seen.add(url)
        result.append((url, "official_logo"))
    return result
def extract_logo_asset(html: str, page_url: str) -> tuple[str, str] | None:
    assets = extract_logo_assets(html, page_url)
    return assets[0] if assets else None
def extract_logo_url(html: str, page_url: str) -> str | None:
    asset = extract_logo_asset(html, page_url)
    return asset[0] if asset else None
