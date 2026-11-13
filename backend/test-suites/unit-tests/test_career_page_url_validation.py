import socket

import pytest

from scout.crawling.career_page_url_validation import (
    UnsafeCareerPageUrl,
    validate_public_career_url,
)


def test_rejects_non_https_and_local_urls() -> None:
    for value in ("http://example.com/careers", "https://localhost/jobs"):
        with pytest.raises(UnsafeCareerPageUrl):
            validate_public_career_url(value)


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
    assert validate_public_career_url("https://careers.example.com/jobs").endswith("/jobs")
