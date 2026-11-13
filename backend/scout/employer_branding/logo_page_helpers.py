import re
from urllib.parse import urlparse

import httpx

from scout.employer_branding.logo_ai_verification import (
    LogoAIUnavailable,
    assess_logo_image,
)
from scout.employer_branding.logo_http import (
    MAX_IMAGE_BYTES,
    fetch_public_resource,
)
from scout.employer_branding.logo_image_validation import has_usable_logo_dimensions
from scout.employer_branding.logo_page_url_validation import is_ats_careers_host
from scout.settings import get_settings

_MULTI_LABEL_SUFFIXES = {"co.za", "co.uk", "com.au", "co.nz", "com.sg"}


def root_domain(host: str) -> str:
    labels = host.casefold().removeprefix("www.").split(".")
    suffix = ".".join(labels[-2:])
    count = 3 if suffix in _MULTI_LABEL_SUFFIXES else 2
    return ".".join(labels[-count:])


def same_employer_host(first: str, second: str) -> bool:
    return root_domain(httpx.URL(first).host) == root_domain(httpx.URL(second).host)


def registered_redirect(final_url: str, allowed_hosts: list[str]) -> bool:
    final_host = httpx.URL(final_url).host.casefold()
    if is_ats_careers_host(final_url):
        return any(
            httpx.URL(host).host.casefold() == final_host for host in allowed_hosts
        )
    final_root = root_domain(final_host)
    return any(root_domain(host) == final_root for host in allowed_hosts)


def workday_logo_url(page_url: str) -> str | None:
    parsed = urlparse(page_url)
    host = (parsed.hostname or "").casefold()
    if not host.endswith(".myworkdayjobs.com"):
        return None
    ignored = {"jobs", "search", "wday", "cxs"}
    site = next((part for part in parsed.path.split("/") if part
        and not re.fullmatch(r"(?i)en-[a-z]{2}", part)
        and part.casefold() not in ignored), None)
    return f"https://{host}/{site}/assets/logo" if site and re.fullmatch(
        r"[A-Za-z0-9_-]+", site
    ) else None


async def fetch_workday_logo(client, page_url):
    logo_url = workday_logo_url(page_url)
    if not logo_url:
        return None
    image = await fetch_public_resource(client, logo_url, "image/", MAX_IMAGE_BYTES)
    if not has_usable_logo_dimensions(image.content, image.content_type):
        return None
    return image.url, page_url, "official_ats_logo"


async def ai_accepts_image(image, employer_name, diagnostics):
    settings = get_settings()
    if not settings.ai_enabled or image.content_type == "image/svg+xml":
        return True
    try:
        result = await assess_logo_image(
            image.content, image.content_type, employer_name
        )
    except LogoAIUnavailable as error:
        reason = (\n            "AI_ASSESSMENT_LIMIT" if "limit" in str(error)\n            else "AI_VERIFICATION_UNAVAILABLE"\n        )
        diagnostics.append(reason)
        return False
    if not result.is_logo or result.confidence < 0.82:
        diagnostics.append("AI_REJECTED_IMAGE")
        return False
    return True
