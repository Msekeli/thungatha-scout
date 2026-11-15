from scout.employer_branding.logo_ai_clients import rasterize_svg_for_ai
from scout.employer_branding.logo_ai_verification import (
    LogoAIUnavailable,
    assess_logo_image,
)
from scout.settings import get_settings


async def ai_accepts_image(image, employer_name, diagnostics):
    settings = get_settings()
    if not settings.ai_enabled:
        diagnostics.append("AI_VERIFICATION_DISABLED")
        return True
    content, mime = image.content, image.content_type
    if mime == "image/svg+xml":
        try:
            content, mime = rasterize_svg_for_ai(content), "image/png"
        except Exception as error:
            diagnostics.append(f"AI_SVG_RASTERIZATION_FAILED:{type(error).__name__}")
            diagnostics.append("DETERMINISTIC_FALLBACK_ACCEPTED")
            return True
    try:
        result = await assess_logo_image(content, mime, employer_name)
    except LogoAIUnavailable as error:
        reason = (
            "AI_ASSESSMENT_LIMIT"
            if "limit" in str(error)
            else "AI_VERIFICATION_UNAVAILABLE"
        )
        diagnostics.extend([reason, "DETERMINISTIC_FALLBACK_ACCEPTED"])
        return True
    if not result.is_logo or result.confidence < 0.82:
        diagnostics.append("AI_REJECTED_IMAGE")
        return False
    return True
