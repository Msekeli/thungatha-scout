import re


def has_usable_logo_dimensions(content: bytes, content_type: str) -> bool:
    if content.startswith((b"GIF87a", b"GIF89a")):
        return False
    if content_type == "image/svg+xml":
        svg = content[:8192].decode("utf-8", errors="ignore")
        viewbox = re.search(
            r'viewBox=["\']\s*[\d.]+[ ,]+[\d.]+[ ,]+([\d.]+)[ ,]+([\d.]+)',
            svg, re.I,
        )
        if viewbox:
            return min(float(viewbox.group(1)), float(viewbox.group(2))) >= 24
        width = re.search(r'width=["\']([\d.]+)', svg, re.I)
        height = re.search(r'height=["\']([\d.]+)', svg, re.I)
        return bool(width and height and min(float(width.group(1)), float(height.group(1))) >= 24)
    if content.startswith(b"\x89PNG") and len(content) >= 24:
        width = int.from_bytes(content[16:20], "big")
        height = int.from_bytes(content[20:24], "big")
        return min(width, height) >= 24
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return len(content) >= 30
    if content.startswith(b"\xff\xd8"):
        return len(content) >= 256
    return False
