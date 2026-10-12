"""Generuje build/jolaos.ico (pochodnia) bez zewnętrznych bibliotek."""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

SIZES = (256, 64, 48, 32, 16)
BG = (31, 41, 55)  # grafit
FLAME_OUTER = (234, 88, 12)
FLAME_INNER = (251, 191, 36)
FLAME_CORE = (254, 243, 199)
HANDLE = (120, 72, 36)
HANDLE_DARK = (87, 50, 24)


def _in_flame(nx: float, ny: float, scale: float) -> bool:
    """Płomień jako kropla: szeroka u dołu, ostra u góry. Współrzędne w [0,1]."""
    cx, top, bottom = 0.5, 0.08, 0.60
    if not top <= ny <= bottom:
        return False
    tt = (ny - top) / (bottom - top)
    half = scale * 0.26 * math.sin(math.pi * tt**0.72)
    return abs(nx - cx) <= half


def _in_handle(nx: float, ny: float) -> bool:
    return 0.44 <= nx <= 0.56 and 0.58 <= ny <= 0.90


def render(size: int) -> bytes:
    rows = []
    r = size / 2
    for y in range(size):
        row = bytearray([0])  # filtr PNG: brak
        for x in range(size):
            px, py = x + 0.5, y + 0.5
            nx, ny = px / size, py / size
            dist = math.hypot(px - r, py - r)
            if dist > r:
                row += bytes((0, 0, 0, 0))
                continue
            color = BG
            if _in_handle(nx, ny):
                color = HANDLE_DARK if nx < 0.47 else HANDLE
            if _in_flame(nx, ny, 1.0):
                color = FLAME_OUTER
            if _in_flame(nx, ny + 0.06, 0.62):
                color = FLAME_INNER
            if _in_flame(nx, ny + 0.12, 0.30):
                color = FLAME_CORE
            # miękka krawędź koła
            alpha = 255 if dist < r - 1 else int(255 * max(0.0, r - dist))
            row += bytes((*color, alpha))
        rows.append(bytes(row))
    return png(size, size, b"".join(rows))


def png(width: int, height: int, raw: bytes) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def ico(images: list[tuple[int, bytes]]) -> bytes:
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries = b""
    blobs = b""
    for size, data in images:
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(data), offset)
        blobs += data
        offset += len(data)
    return header + entries + blobs


def main() -> None:
    out = Path(__file__).with_name("jolaos.ico")
    out.write_bytes(ico([(s, render(s)) for s in SIZES]))
    print(out)


if __name__ == "__main__":
    main()
