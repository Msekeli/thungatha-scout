import httpx

from scout.employer_branding.logo_http import (
    MAX_IMAGE_BYTES,
    InvalidLogoAsset,
    UnavailableLogoAsset,
    fetch_public_resource,
)
from scout.employer_branding.logo_image_validation import has_usable_logo_dimensions
from scout.employer_branding.logo_page_helpers import ai_accepts_image


async def validate_crawlee_candidates(
    candidates: list[tuple[str, str, str]],
    employer_name: str,
    diagnostics: list[str],
) -> tuple[str, str, str] | None:
    async with httpx.AsyncClient(
        timeout=12, follow_redirects=False, trust_env=False
    ) as client:
        for candidate, source_url, logo_type in candidates[:8]:
            try:
                image = await fetch_public_resource(
                    client, candidate, "image/", MAX_IMAGE_BYTES
                )
                if not has_usable_logo_dimensions(image.content, image.content_type):
                    diagnostics.append("IMAGE_DIMENSIONS_REJECTED")
                    continue
                if await ai_accepts_image(image, employer_name, diagnostics):
                    return image.url, source_url, logo_type
            except InvalidLogoAsset:
                diagnostics.append("IMAGE_INVALID")
            except (UnavailableLogoAsset, httpx.HTTPError, OSError):
                diagnostics.append("IMAGE_UNAVAILABLE")
    return None
