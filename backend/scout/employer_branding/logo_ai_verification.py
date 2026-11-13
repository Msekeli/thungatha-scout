import asyncio
import hashlib

from scout.employer_branding.logo_ai_clients import (
    LogoAssessment,
    classify_with_provider,
)
from scout.settings import get_settings

_CACHE: dict[str, LogoAssessment] = {}


class LogoAIUnavailable(RuntimeError):
    pass


async def assess_logo_image(image: bytes, mime: str, employer: str) -> LogoAssessment:
    settings = get_settings()
    if not settings.ai_enabled:
        raise LogoAIUnavailable("AI logo verification is disabled")
    digest = hashlib.sha256(
        b"logo-vision-v1" + employer.casefold().encode() + mime.encode() + image
    ).hexdigest()
    if digest in _CACHE:
        return _CACHE[digest]
    providers = [settings.ai_primary_provider]
    if settings.ai_fallback_enabled:
        providers.append("groq" if providers[0] == "gemini" else "gemini")
    errors = []
    for provider in providers:
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    classify_with_provider, provider, image, mime, employer, settings
                ),
                timeout=settings.ai_timeout_seconds,
            )
            _CACHE[digest] = result
            if len(_CACHE) > 128:
                _CACHE.pop(next(iter(_CACHE)))
            return result
        except Exception as error:
            errors.append(f"{provider}: {type(error).__name__}")
    raise LogoAIUnavailable("; ".join(errors) or "No AI provider available")
