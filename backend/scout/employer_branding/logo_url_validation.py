import ipaddress
import socket
from urllib.parse import urlparse


BLOCKED_HOSTS = {
    "google.com",
    "www.google.com",
    "favicons.githubusercontent.com",
    "greenhouse.io",
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
    "jobs.lever.co",
    "lever.co",
    "teamtailor.com",
    "workable.com",
}
MAX_IMAGE_BYTES = 2_000_000


class InvalidLogoAsset(ValueError):
    pass


class UnavailableLogoAsset(RuntimeError):
    pass


def is_usable_employer_logo_url(value: str | None) -> bool:
    if not value:
        return False
    try:
        parsed = urlparse(value)
        host = (parsed.hostname or "").casefold().rstrip(".")
        blocked = host in BLOCKED_HOSTS or host.endswith(
            (
                ".greenhouse.io",
                ".lever.co",
                ".teamtailor.com",
                ".myworkdayjobs.com",
                ".workable.com",
            )
        )
        return (
            parsed.scheme == "https"
            and bool(host)
            and not parsed.username
            and not parsed.password
            and parsed.port in (None, 443)
            and not blocked
        )
    except ValueError:
        return False


def validate_public_logo_url(value: str) -> None:
    if not is_usable_employer_logo_url(value):
        raise InvalidLogoAsset("URL is not an allowed public HTTPS URL.")
    host = urlparse(value).hostname
    try:
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as error:
        raise UnavailableLogoAsset("Host DNS lookup failed.") from error
    if not addresses or any(
        not ipaddress.ip_address(item[4][0]).is_global for item in addresses
    ):
        raise InvalidLogoAsset("URL resolves to a non-public network.")


def is_valid_image_payload(content: bytes, content_type: str) -> bool:
    signatures = (
        b"\x89PNG\r\n\x1a\n",
        b"\xff\xd8\xff",
        b"GIF87a",
        b"GIF89a",
        b"BM",
        b"II*\x00",
        b"MM\x00*",
        b"\x00\x00\x01\x00",
    )
    if any(content.startswith(signature) for signature in signatures):
        return True
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return True
    if content_type.casefold() == "image/svg+xml":
        text = content[:4096].decode("utf-8", errors="ignore").casefold()
        return "<svg" in text and "<!doctype" not in text and "<!entity" not in text
    return False
