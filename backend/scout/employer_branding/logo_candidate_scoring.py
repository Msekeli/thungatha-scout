import re
from urllib.parse import urlparse


_EXCLUDED = (
    "favicon",
    "apple-touch",
    "avatar",
    "social",
    "share",
    "banner",
    "preview",
    "hero",
    "loading",
    "loader",
    "spinner",
)
_HINTS = ("logo", "brandmark", "brand-mark", "wordmark", "brand mark")


def _tokens(value: str) -> set[str]:
    return {part.casefold() for part in re.findall(r"[a-zA-Z0-9]+", value)}


def conflicts_with_employer_name(url: str, employer_name: str) -> bool:
    path = urlparse(url).path.rsplit("/", 1)[-1].casefold()
    words = _tokens(re.sub(r"\.[a-z0-9]+$", "", path))
    ignored = {"logo", "brand", "mark", "word", "white", "dark"}
    employer_words = _tokens(employer_name)
    brand_words = {
        word
        for word in words - ignored
        if (word.isalpha() and len(word) >= 3) or word in employer_words
    }
    overlap = any(
        a == b or a.startswith(b) or b.startswith(a)
        for a in brand_words
        for b in employer_words
    )
    return bool(employer_name.strip()) and bool(brand_words) and not overlap


def score_logo_candidate(value: str, hint: str, explicit: bool = False) -> int:
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
