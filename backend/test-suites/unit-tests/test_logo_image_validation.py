from scout.employer_branding.logo_image_validation import has_usable_logo_dimensions
from scout.employer_branding.logo_url_validation import is_valid_image_payload

PNG = (
    b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
    + (200).to_bytes(4, "big") + (80).to_bytes(4, "big") + b"\x00" * 8
)


def test_png_signature_and_dimensions_are_validated() -> None:
    assert is_valid_image_payload(PNG, "image/png")
    assert has_usable_logo_dimensions(PNG, "image/png")


def test_invalid_png_signature_is_rejected() -> None:
    assert not is_valid_image_payload(b"not an image", "image/png")
    assert not has_usable_logo_dimensions(b"not an image", "image/png")
