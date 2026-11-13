def is_valid_image_payload(content: bytes, content_type: str) -> bool:
    signatures = (
        b"\x89PNG\r\n\x1a\n",
        b"\xff\xd8\xff",
        b"GIF87a",
        b"GIF89a",
        b"BM",
        b"II*\x00",
        b"MM\x00*",
        b"\x00\x00\x01\x00",
    )
    if any(content.startswith(signature) for signature in signatures):
        return True
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return True
    if content_type.casefold() == "image/svg+xml":
        text = content[:4096].decode("utf-8", errors="ignore").casefold()
        return "<svg" in text and "<!doctype" not in text and "<!entity" not in text
    return False
