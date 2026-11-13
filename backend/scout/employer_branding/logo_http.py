from dataclasses import dataclass
from typing import Literal
from urllib.parse import urljoin

import httpx

from scout.employer_branding.logo_url_validation import (
    InvalidLogoAsset,
    MAX_IMAGE_BYTES,
    UnavailableLogoAsset,
    is_usable_employer_logo_url,
    is_valid_image_payload,
    validate_public_logo_page_url,
    validate_public_logo_url,
)


@dataclass(frozen=True)
class PublicResource:
    url: str
    content_type: str
    content: bytes


async def fetch_public_resource(
    client: httpx.AsyncClient,
    value: str,
    content_prefix: str,
    max_bytes: int,
    allow_ats_page: bool = False,
) -> PublicResource:
    current = value
    for _ in range(5):
        if allow_ats_page and content_prefix == "text/html":
            validate_public_logo_page_url(current)
        else:
            validate_public_logo_url(current)
        async with client.stream("GET", current) as response:
            if response.status_code in {301, 302, 303, 307, 308}:
                location = response.headers.get("location")
                if not location:
                    raise InvalidLogoAsset("Redirect has no destination.")
                current = urljoin(current, location)
                continue
            if 300 <= response.status_code < 400:
                raise InvalidLogoAsset("Unexpected redirect response.")
            if (
                response.status_code in {401, 403, 408, 425, 429}
                or response.status_code >= 500
            ):
                raise UnavailableLogoAsset("Remote host is temporarily unavailable.")
            if response.status_code >= 400:
                raise InvalidLogoAsset("Remote resource was not found.")
            content_type = response.headers.get("content-type", "").split(";")[0]
            if not content_type.casefold().startswith(content_prefix):
                raise InvalidLogoAsset(
                    "Remote resource has an unexpected content type."
                )
            length = response.headers.get("content-length")
            if length:
                try:
                    if int(length) > max_bytes:
                        raise InvalidLogoAsset(
                            "Remote resource exceeds the size limit."
                        )
                except ValueError as error:
                    raise InvalidLogoAsset("Invalid content length.") from error
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > max_bytes:
                    raise InvalidLogoAsset("Remote resource exceeds the size limit.")
            content = bytes(body)
            if content_prefix == "image/" and not is_valid_image_payload(
                content, content_type
            ):
                raise InvalidLogoAsset("Remote response is not valid image content.")
            return PublicResource(str(response.url), content_type, content)
    raise InvalidLogoAsset("Too many redirects.")


async def inspect_existing_logo(
    value: str | None,
) -> Literal["missing", "valid", "invalid", "unknown"]:
    if not value:
        return "missing"
    if not is_usable_employer_logo_url(value):
        return "invalid"
    async with httpx.AsyncClient(
        timeout=8, follow_redirects=False, trust_env=False
    ) as client:
        try:
            await fetch_public_resource(client, value, "image/", MAX_IMAGE_BYTES)
            return "valid"
        except InvalidLogoAsset:
            return "invalid"
        except (UnavailableLogoAsset, httpx.HTTPError, OSError):
            return "unknown"
