import asyncio

import pytest

from scout.employer_branding import logo_ai_verification as verification
from scout.employer_branding.logo_ai_clients import LogoAssessment
from scout.settings import Settings


def settings() -> Settings:
    return Settings(
        ai_enabled=True, ai_primary_provider="gemini", ai_fallback_enabled=True,
        ai_timeout_seconds=2, gemini_api_key="test", gemini_model="vision",
        groq_api_key="test", groq_model="vision",
    )


def test_uses_primary_provider_and_caches_result(monkeypatch) -> None:
    verification._CACHE.clear()
    monkeypatch.setattr(verification, "get_settings", settings)
    calls = []

    def classify(provider, image, mime, employer, config):
        calls.append(provider)
        return LogoAssessment(is_logo=True, confidence=0.96, reason="Wordmark")

    monkeypatch.setattr(verification, "classify_with_provider", classify)
    first = asyncio.run(verification.assess_logo_image(b"image", "image/png", "Damen"))
    second = asyncio.run(verification.assess_logo_image(b"image", "image/png", "Damen"))
    assert first == second
    assert calls == ["gemini"]


def test_falls_back_when_primary_provider_fails(monkeypatch) -> None:
    verification._CACHE.clear()
    monkeypatch.setattr(verification, "get_settings", settings)
    calls = []

    def classify(provider, image, mime, employer, config):
        calls.append(provider)
        if provider == "gemini":
            raise RuntimeError("quota")
        return LogoAssessment(is_logo=False, confidence=0.99, reason="Photograph")

    monkeypatch.setattr(verification, "classify_with_provider", classify)
    result = asyncio.run(
        verification.assess_logo_image(b"photo", "image/jpeg", "Damen")
    )
    assert not result.is_logo
    assert calls == ["gemini", "groq"]


def test_disabled_ai_does_not_call_provider(monkeypatch) -> None:
    verification._CACHE.clear()
    monkeypatch.setattr(verification, "get_settings", lambda: Settings())
    with pytest.raises(verification.LogoAIUnavailable):
        asyncio.run(verification.assess_logo_image(b"image", "image/png", "Damen"))
