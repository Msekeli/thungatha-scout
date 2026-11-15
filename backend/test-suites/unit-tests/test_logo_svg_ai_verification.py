import asyncio
from types import SimpleNamespace

from scout.employer_branding import logo_ai_image_assessment
from scout.employer_branding.logo_ai_clients import LogoAssessment
from scout.employer_branding.logo_http import PublicResource


def test_svg_is_rasterized_before_ai_assessment(monkeypatch) -> None:
    monkeypatch.setattr(
        logo_ai_image_assessment, "get_settings",
        lambda: SimpleNamespace(ai_enabled=True),
    )
    monkeypatch.setattr(
        logo_ai_image_assessment, "rasterize_svg_for_ai",
        lambda content: b"rasterized-png",
    )
    received = []

    async def assess(content, mime, employer):
        received.append((content, mime, employer))
        return LogoAssessment(
            is_logo=True, confidence=0.98, reason="Official wordmark"
        )

    monkeypatch.setattr(logo_ai_image_assessment, "assess_logo_image", assess)
    image = PublicResource(
        "https://cdn.example.com/logo.svg",
        "image/svg+xml",
        b"<svg xmlns='http://www.w3.org/2000/svg'></svg>",
    )
    diagnostics = []

    accepted = asyncio.run(
        logo_ai_image_assessment.ai_accepts_image(image, "Example Ltd", diagnostics)
    )

    assert accepted is True
    assert received == [(b"rasterized-png", "image/png", "Example Ltd")]
    assert diagnostics == []


def test_svg_rasterization_failure_uses_deterministic_fallback(monkeypatch) -> None:
    monkeypatch.setattr(
        logo_ai_image_assessment, "get_settings",
        lambda: SimpleNamespace(ai_enabled=True),
    )

    def fail_rasterization(content):
        raise ValueError("unsupported SVG")

    monkeypatch.setattr(
        logo_ai_image_assessment, "rasterize_svg_for_ai", fail_rasterization
    )
    image = PublicResource(
        "https://cdn.example.com/logo.svg", "image/svg+xml", b"<svg/>"
    )
    diagnostics = []

    accepted = asyncio.run(
        logo_ai_image_assessment.ai_accepts_image(image, "Example Ltd", diagnostics)
    )

    assert accepted is True
    assert diagnostics == [
        "AI_SVG_RASTERIZATION_FAILED:ValueError",
        "DETERMINISTIC_FALLBACK_ACCEPTED",
    ]
