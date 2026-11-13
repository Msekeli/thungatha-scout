import asyncio
import socket

import httpx
import pytest

from scout.employer_branding.logo_http import (
    InvalidLogoAsset,
    fetch_public_resource,
)


def test_rejects_non_public_dns_results(monkeypatch) -> None:
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("10.0.0.2", 443))],
    )

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, content=b"")
            )
        ) as client:
            with pytest.raises(InvalidLogoAsset):
                await fetch_public_resource(
                    client, "https://cdn.example.com/a.png", "image/", 100
                )

    asyncio.run(run())


def test_rejects_redirects_to_blocked_ats_hosts(monkeypatch) -> None:
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("8.8.8.8", 443))],
    )

    async def handler(request):
        return httpx.Response(
            302, headers={"location": "https://apply.workable.com/logo"}
        )

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(InvalidLogoAsset):
                await fetch_public_resource(
                    client, "https://cdn.example.com/a.png", "image/", 100
                )

    asyncio.run(run())


def test_rejects_invalid_image_bytes(monkeypatch) -> None:
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("8.8.8.8", 443))],
    )

    async def handler(request):
        return httpx.Response(
            200, headers={"content-type": "image/png"}, content=b"not png"
        )

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(InvalidLogoAsset):
                await fetch_public_resource(
                    client, "https://cdn.example.com/a.png", "image/", 100
                )

    asyncio.run(run())


def test_rejects_riff_audio_disguised_as_webp(monkeypatch) -> None:
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("8.8.8.8", 443))],
    )

    async def handler(request):
        return httpx.Response(
            200,
            headers={"content-type": "image/webp"},
            content=b"RIFF" + b"\x00" * 4 + b"WAVE",
        )

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(InvalidLogoAsset):
                await fetch_public_resource(
                    client, "https://cdn.example.com/a.webp", "image/", 100
                )

    asyncio.run(run())
