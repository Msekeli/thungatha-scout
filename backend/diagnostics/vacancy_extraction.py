"""Deterministic vacancy-link and card-context extraction shared by diagnostics."""
from __future__ import annotations

import re
from urllib.parse import urlparse

GENERIC_LABEL = re.compile(
    r"^(?:view(?: role(?: details)?| details| vacancy| job)?|details|"
    r"read more|learn more|apply(?: now| for this role)?|open role|"
    r"view position|)$", re.I,
)
NAV_SLUGS = {
    "about", "benefits", "career-planning", "careers", "culture", "faq",
    "join-us", "library", "life-at", "skill-hub", "team", "why-join-us",
}
ROLE_SIGNAL = re.compile(
    r"engineer|developer|analyst|designer|manager|lead|consultant|architect|"
    r"tester|\bqa\b|intern|graduate|programme|program|product owner|"
    r"coordinator|scientist|specialist|technician|operator|administrator|"
    r"accountant|sales|support|director|officer|recruiter|devops|software|"
    r"java|python|javascript|mobile|data|cloud|platform|security|network|"
    r"technical|frontend|backend|full.?stack|ux/ui|afn", re.I,
)
LOCATION = re.compile(
    r"\b(Cape Town|Stellenbosch|Johannesburg|Pretoria|Durban|Bellville|"
    r"Port Elizabeth|Gqeberha|East London|Bloemfontein|George|Paarl|"
    r"Midrand|Sandton|Centurion|South Africa|remote|hybrid)\b"
    r"(?:\s*,?\s*South Africa)?(?:\s*\([^)]*\))?", re.I,
)
EMPLOYMENT = re.compile(
    r"\b(full[- ]time|part[- ]time|permanent|contract|internship|"
    r"fixed[- ]term|graduate programme|graduate program|hybrid|remote)\b", re.I,
)
CLOSING_DATE = re.compile(
    r"(?:closes?|closing date)\s*:?\s*"
    r"(\d{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{1,2},?\s+\d{4})", re.I,
)
CTA_END = re.compile(
    r"\s*(?:view role details|view role|view details|read more|learn more|"
    r"apply now|apply for this role|apply|view|details)\s*$", re.I,
)
CATEGORY_TITLE = re.compile(
    r"^(.+?)\s+(?:Software Engineering|Operations|Engineering|Developer|"
    r"UX/UI Designer|Product Owner)\s*[·|]", re.I,
)


def _normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _slug_title(url: str) -> str:
    slug = urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
    slug = re.sub(r"[-_]+", " ", slug)
    slug = re.sub(r"\s+(?:sa|ind)\d{2}(?:\s+[a-z0-9]+)*$", "", slug, flags=re.I)
    return _normalise(slug).title()


def _has_card_evidence(card: str) -> bool:
    return bool(card and (LOCATION.search(card) or EMPLOYMENT.search(card)
                          or CLOSING_DATE.search(card)))


def is_vacancy_detail_url(url: str, card: str = "", label: str = "") -> bool:
    """Accept known detail-route shapes while rejecting generic career navigation."""
    parts = [part for part in urlparse(url).path.strip("/").split("/") if part]
    if len(parts) < 2:
        return False
    root, slug = parts[0].casefold(), parts[1].casefold()
    if slug in NAV_SLUGS or not ROLE_SIGNAL.search(slug.replace("-", " ")):
        return False
    if root in {"position", "o", "jobs"}:
        return True
    if root in {"career", "careers"}:
        return bool(ROLE_SIGNAL.search(label) or ROLE_SIGNAL.search(card)
                    or _has_card_evidence(card))
    return False


def extract_vacancy_candidate(
    link: dict, source_url: str, company: str,
    extraction_method: str = "visible_html_link_and_context",
) -> dict | None:
    """Return a reviewable vacancy candidate only when route and title evidence agree."""
    href = _normalise(link.get("href", "")).split("#", 1)[0]
    label = _normalise(link.get("text", ""))
    card = _normalise(link.get("card", ""))
    if not href or not is_vacancy_detail_url(href, card, label):
        return None

    generic = not label or bool(GENERIC_LABEL.fullmatch(label))
    title = ""
    category_match = CATEGORY_TITLE.search(card)
    if category_match:
        title = category_match.group(1).strip(" :-|")
    elif generic:
        cleaned_card = CTA_END.sub("", card).strip(" :-|")
        if cleaned_card:
            first_segment = re.split(r"\s*[·|]\s*", cleaned_card, maxsplit=1)[0]
            if 4 <= len(first_segment) <= 150 and ROLE_SIGNAL.search(first_segment):
                title = first_segment
            elif len(cleaned_card) <= 150 and ROLE_SIGNAL.search(cleaned_card):
                title = cleaned_card
    elif label and len(label) <= 150:
        title = re.split(r"\s*[·|]\s*", label, maxsplit=1)[0].strip()

    if not title:
        title = _slug_title(href)
    title = CTA_END.sub("", _normalise(title)).strip(" :-|")
    title = re.sub(r"\s+(?:Cape Town|Stellenbosch|Johannesburg|Pretoria|Durban|"
                   r"Bellville|South Africa)(?:\s+\w+)?$", "", title, flags=re.I).strip()
    if not 4 <= len(title) <= 150 or not ROLE_SIGNAL.search(title):
        return None

    location_match = LOCATION.search(card)
    date_match = CLOSING_DATE.search(card)
    return {
        "company": company,
        "title": title,
        "location": _normalise(location_match.group(0)) if location_match else None,
        "url": href,
        "source_url": source_url,
        "closing_date_text": date_match.group(1) if date_match else None,
        "extraction_method": extraction_method,
        "evidence_excerpt": card[:600] if card else label[:300],
        "needs_review": True,
    }
