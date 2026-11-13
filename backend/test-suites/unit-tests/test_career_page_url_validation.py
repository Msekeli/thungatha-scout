import socket

import pytest

from scout.crawling.career_page_crawler import validated_discovered_links
from scout.crawling.career_page_url_validation import (
    UnsafeCareerPageUrl,
    validate_public_career_url,
)


def test_rejects_non_https_and_local_urls() -> None:
    for value in ("http://example.com/careers", "https://localhost/jobs"):
        with pytest.raises(UnsafeCareerPageUrl):
            validate_public_career_url(value)


def test_rejects_credentials_and_nonstandard_ports() -> None:
    values = (
        "https://user:pass@example.com/jobs",
        "https://:pass@example.com/jobs",
        "https://example.com:8443/jobs",
    )
    for value in values:
        with pytest.raises(UnsafeCareerPageUrl):
            validate_public_career_url(value)


def test_rejects_invalid_ports() -> None:
    with pytest.raises(UnsafeCareerPageUrl):
        validate_public_career_url("https://example.com:invalid/jobs")


def test_rejects_private_ip_literal() -> None:
    with pytest.raises(UnsafeCareerPageUrl):
        validate_public_career_url("https://10.0.0.8/careers")


def test_rejects_host_resolving_to_private_address(monkeypatch) -> None:
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("192.168.1.2", 443))],
    )
    with pytest.raises(UnsafeCareerPageUrl):
        validate_public_career_url("https://careers.example.com/jobs")


def test_accepts_host_resolving_only_to_public_addresses(monkeypatch) -> None:
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("93.184.216.34", 443))],
    )
    assert validate_public_career_url("https://careers.example.com/jobs").endswith(
        "/jobs"
    )


def test_discovered_links_are_revalidated(monkeypatch) -> None:
    def resolve(host, *args, **kwargs):
        address = "192.168.1.2" if host == "internal.example" else "93.184.216.34"
        return [(None, None, None, None, (address, 443))]

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    links = validated_discovered_links(
        ("https://public.example/jobs", "https://internal.example/jobs")
    )
    assert links == ["https://public.example/jobs"]
