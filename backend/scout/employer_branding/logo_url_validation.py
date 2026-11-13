import ipaddress
import socket

from scout.employer_branding.logo_image_payload_validation import is_valid_image_payload
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


def _valid_public_https_url(value: str | None) -> bool:
    if not value:
        return False
    try:
        parsed = urlparse(value)
        host = (parsed.hostname or "").casefold().rstrip(".")
        return (
            parsed.scheme == "https"
            and bool(host)
            and not parsed.username
            and not parsed.password
            and parsed.port in (None, 443)
        )
    except ValueError:
        return False


def _is_trusted_ats_logo_path(value: str) -> bool:
    parsed = urlparse(value)
    host = (parsed.hostname or "").casefold().rstrip(".")
    path = parsed.path.rstrip("/")
    if host.endswith(".myworkdayjobs.com"):
        return path.endswith("/assets/logo")
    return host == "recruiting.cdn.greenhouse.io" and (
        "/external_greenhouse_job_boards/logos/" in path
    )


def is_usable_employer_logo_url(value: str | None) -> bool:
    if not _valid_public_https_url(value):
        return False
    if _is_trusted_ats_logo_path(value or ""):
        return True
    host = (urlparse(value).hostname or "").casefold().rstrip(".")
    blocked = host in BLOCKED_HOSTS or any(
        host.endswith(suffix)
        for suffix in (
            ".greenhouse.io",
            ".lever.co",
            ".teamtailor.com",
            ".myworkdayjobs.com",
            ".workable.com",
        )
    )
    return not blocked


def _validate_public_host(value: str) -> None:
    host = urlparse(value).hostname
    try:
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as error:
        raise UnavailableLogoAsset("Host DNS lookup failed.") from error
    if not addresses or any(
        not ipaddress.ip_address(item[4][0]).is_global for item in addresses
    ):
        raise InvalidLogoAsset("URL resolves to a non-public network.")


def validate_public_logo_url(value: str) -> None:
    if not is_usable_employer_logo_url(value):
        raise InvalidLogoAsset("URL is not an allowed public HTTPS image URL.")
    _validate_public_host(value)
