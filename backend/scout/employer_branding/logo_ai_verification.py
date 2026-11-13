import asyncio
import base64
import hashlib
import json

from pydantic import BaseModel, Field, ValidationError

from scout.settings import get_settings

_PROMPT = (
    "Decide whether this image is the official logo or wordmark of "
    "{employer}. Reject photographs, people, buildings, products, "
    "screenshots, banners, social cards, generic illustrations and other "
    "brands. Return only JSON: is_logo, confidence from 0 to 1, reason."
)
_CACHE: dict[str, "LogoAssessment"] = {}


class LogoAssessment(BaseModel):
    is_logo: bool
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(max_length=240)


class LogoAIUnavailable(RuntimeError):
    pass


def _gemini(image: bytes, mime: str, prompt: str, model: str, key: str):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model=model,
        contents=[prompt, types.Part.from_bytes(data=image, mime_type=mime)],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LogoAssessment,
            max_output_tokens=256,
            temperature=0,
        ),
    )
    return LogoAssessment.model_validate_json(response.text or "")


def _groq(image: bytes, mime: str, prompt: str, model: str, key: str):
    from groq import Groq

    data = base64.b64encode(image).decode("ascii")
    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=256,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {
                "url": f"data:{mime};base64,{data}"
            }},
        ]}],
    )
    return LogoAssessment.model_validate_json(
        response.choices[0].message.content or ""
    )


def _provider(name, image, mime, prompt, settings):
    if name == "gemini":
        key, model = settings.gemini_api_key, settings.gemini_model
        call = _gemini
    else:
        key, model = settings.groq_api_key, settings.groq_model
        call = _groq
    if not key or not model:
        raise LogoAIUnavailable(f"{name} key/model is not configured")
    return call(image, mime, prompt, model, key.get_secret_value())


async def assess_logo_image(
    image: bytes, mime: str, employer_name: str
) -> LogoAssessment:
    settings = get_settings()
    if not settings.ai_enabled:
        raise LogoAIUnavailable("AI logo verification is disabled")
    digest = hashlib.sha256(
        employer_name.casefold().encode() + mime.encode() + image
    ).hexdigest()
    if digest in _CACHE:
        return _CACHE[digest]
    prompt = _PROMPT.format(employer=employer_name)
    providers = [settings.ai_primary_provider]
    fallback = "groq" if providers[0] == "gemini" else "gemini"
    if settings.ai_fallback_enabled:
        providers.append(fallback)
    errors = []
    for provider in providers:
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    _provider, provider, image, mime, prompt, settings
                ),
                timeout=settings.ai_timeout_seconds,
            )
            _CACHE[digest] = result
            if len(_CACHE) > 128:
                _CACHE.pop(next(iter(_CACHE)))
            return result
        except (Exception, ValidationError) as error:
            errors.append(f"{provider}: {type(error).__name__}")
    raise LogoAIUnavailable("; ".join(errors) or "No AI provider available")
