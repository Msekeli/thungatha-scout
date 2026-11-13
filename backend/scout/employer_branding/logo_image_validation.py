import re


def _jpeg_dimensions(data: bytes) -> tuple[int, int]:
    index = 2
    markers = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    while index + 9 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9, 0x01} or 0xD0 <= marker <= 0xD7:
            continue
        size = int.from_bytes(data[index : index + 2], "big")
        if marker in markers and size >= 7:
            height = int.from_bytes(data[index + 3 : index + 5], "big")
            width = int.from_bytes(data[index + 5 : index + 7], "big")
            return width, height
        if size < 2:
            break
        index += size
    return 0, 0


def _webp_dimensions(data: bytes) -> tuple[int, int]:
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height
    if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        return 1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF)
    if chunk == b"VP8 " and len(data) >= 30:
        width = int.from_bytes(data[26:28], "little") & 0x3FFF
        height = int.from_bytes(data[28:30], "little") & 0x3FFF
        return width, height
    return 0, 0


def has_usable_logo_dimensions(content: bytes, content_type: str) -> bool:
    if content.startswith((b"GIF87a", b"GIF89a")):
        return False
    if content_type == "image/svg+xml":
        svg = content[:8192].decode("utf-8", errors="ignore")
        viewbox = re.search(
            r'viewBox=["\']\s*[\d.]+[ ,]+[\d.]+[ ,]+([\d.]+)[ ,]+([\d.]+)',
            svg,
            re.I,
        )
        if viewbox:
            return min(float(viewbox.group(1)), float(viewbox.group(2))) >= 24
        width = re.search(r'width=["\']([\d.]+)', svg, re.I)
        height = re.search(r'height=["\']([\d.]+)', svg, re.I)
        return bool(
            width
            and height
            and min(float(width.group(1)), float(height.group(1))) >= 24
        )
    if content.startswith(b"\x89PNG") and len(content) >= 24:
        width = int.from_bytes(content[16:20], "big")
        height = int.from_bytes(content[20:24], "big")
    elif content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        width, height = _webp_dimensions(content)
    elif content.startswith(b"\xff\xd8"):
        width, height = _jpeg_dimensions(content)
    else:
        return False
    return min(width, height) >= 24
