import base64

from pydantic import BaseModel, Field

_PROMPT = (
    "Is this image the official logo or wordmark of {employer}? Reject "
    "photographs, people, buildings, products, screenshots, banners, "
    "social cards, illustrations and other brands. Return JSON with "
    "is_logo, confidence (0-1), and reason."
)


class LogoAssessment(BaseModel):
    is_logo: bool
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(max_length=240)


def gemini_assessment(image, mime, prompt, model, key, timeout):
    from google import genai
    from google.genai import types

    client = genai.Client(\n        api_key=key, http_options=types.HttpOptions(timeout=timeout * 1000)\n    )\n    response = client.models.generate_content(
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


def groq_assessment(image, mime, prompt, model, key, timeout):
    from groq import Groq

    data = base64.b64encode(image).decode("ascii")
    response = Groq(api_key=key, timeout=timeout).chat.completions.create(
        model=model, temperature=0, max_tokens=256,
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


def classify_with_provider(name, image, mime, employer, settings):
    key, model = (
        (settings.gemini_api_key, settings.gemini_model)
        if name == "gemini"
        else (settings.groq_api_key, settings.groq_model)
    )
    if not key or not model:
        raise RuntimeError(f"{name} key/model is not configured")
    prompt = _PROMPT.format(employer=employer)
    call = gemini_assessment if name == "gemini" else groq_assessment
    return call(\n        image, mime, prompt, model, key.get_secret_value(),\n        settings.ai_timeout_seconds,\n    )
