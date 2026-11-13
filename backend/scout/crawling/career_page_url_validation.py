import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeCareerPageUrl(ValueError):
    """Raised when a career-page URL does not resolve to a public HTTPS target."""


def validate_public_career_url(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or not parsed.hostname or parsed.username:
        raise UnsafeCareerPageUrl("A public HTTPS careers URL is required.")
    host = parsed.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith(".localhost"):
        raise UnsafeCareerPageUrl("Local and private network targets are not allowed.")
    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        try:
            records = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        except OSError as exception:
            raise UnsafeCareerPageUrl(
                "The careers host could not be resolved."
            ) from exception
        addresses = {ipaddress.ip_address(record[4][0]) for record in records}
    if not addresses or any(not address.is_global for address in addresses):
        raise UnsafeCareerPageUrl(
            "The careers host must resolve only to public IP addresses."
        )
    return value.strip()
