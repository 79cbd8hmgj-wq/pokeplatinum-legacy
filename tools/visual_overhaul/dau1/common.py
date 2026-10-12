"""Shared primitives: status vocabulary, bounded reader, LZ10/LZ11, hashing."""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path

# Catalog status vocabulary (DAU1_SPEC workstream 0).
DECODED = "DECODED"                  # real pixels/frames were produced and validated
STRUCTURAL_ONLY = "STRUCTURAL_ONLY"  # container/headers parsed, but no frame-level output
UNSUPPORTED = "UNSUPPORTED"          # input present, format variant not (yet) decodable; evidence recorded
MISSING = "MISSING"                  # a referenced input is absent from the workspace
BLOCKED_INPUT = "BLOCKED_INPUT"      # decoding needs an input that is not accessible at all
STATUSES = (DECODED, STRUCTURAL_ONLY, UNSUPPORTED, MISSING, BLOCKED_INPUT)

# Hard ceilings so hostile or corrupt input can never exhaust memory.
MAX_DECOMPRESSED = 64 * 1024 * 1024
MAX_ENTRIES = 100_000
MAX_CELL_PIXELS = 1024 * 1024


class DecodeError(Exception):
    """A decode failure with a stable machine-readable ``code``."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code
        self.message = message


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


class Reader:
    """Bounds-checked little-endian reader over a bytes-like object."""

    def __init__(self, data: bytes, what: str = "data"):
        self.d = data
        self.what = what

    def __len__(self) -> int:
        return len(self.d)

    def _unpack(self, fmt: str, off: int):
        size = struct.calcsize(fmt)
        if off < 0 or off + size > len(self.d):
            raise DecodeError("TRUNCATED", f"{self.what}: need {size} bytes at 0x{off:x}, size 0x{len(self.d):x}")
        return struct.unpack_from(fmt, self.d, off)[0]

    def u8(self, off): return self._unpack("<B", off)
    def u16(self, off): return self._unpack("<H", off)
    def s16(self, off): return self._unpack("<h", off)
    def u32(self, off): return self._unpack("<I", off)

    def raw(self, off: int, n: int) -> bytes:
        if off < 0 or n < 0 or off + n > len(self.d):
            raise DecodeError("BAD_OFFSET", f"{self.what}: range 0x{off:x}+0x{n:x} outside 0x{len(self.d):x}")
        return self.d[off:off + n]

    def magic(self, off: int, expect: bytes) -> None:
        if self.raw(off, len(expect)) != expect:
            raise DecodeError("BAD_MAGIC", f"{self.what}: expected {expect!r} at 0x{off:x}")


# ----------------------------------------------------------------- LZ (BIOS LZ77 type 0x10 / 0x11)
def lz_decompress(src: bytes, limit: int = MAX_DECOMPRESSED) -> bytes:
    """Bounded DS BIOS LZ10 / LZ11 decompressor.  Never reads or writes outside its limits."""
    if len(src) < 4 or src[0] not in (0x10, 0x11):
        raise DecodeError("BAD_MAGIC", "not an LZ10/LZ11 stream")
    kind = src[0]
    size = src[1] | src[2] << 8 | src[3] << 16
    i = 4
    if size == 0 and kind == 0x11:
        if len(src) < 8:
            raise DecodeError("TRUNCATED", "LZ11 extended size")
        size = int.from_bytes(src[4:8], "little")
        i = 8
    if size > limit:
        raise DecodeError("LIMIT", f"decompressed size {size} exceeds {limit}")
    out = bytearray()
    n = len(src)
    try:
        while len(out) < size:
            flags = src[i]
            i += 1
            for bit in range(8):
                if len(out) >= size:
                    break
                if flags & (0x80 >> bit):
                    a = src[i]
                    if kind == 0x10:
                        length = (a >> 4) + 3
                        disp = ((a & 15) << 8 | src[i + 1]) + 1
                        i += 2
                    else:
                        t = a >> 4
                        if t == 0:
                            length = ((a & 15) << 4 | src[i + 1] >> 4) + 0x11
                            disp = ((src[i + 1] & 15) << 8 | src[i + 2]) + 1
                            i += 3
                        elif t == 1:
                            length = ((a & 15) << 12 | src[i + 1] << 4 | src[i + 2] >> 4) + 0x111
                            disp = ((src[i + 2] & 15) << 8 | src[i + 3]) + 1
                            i += 4
                        else:
                            length = t + 1
                            disp = ((a & 15) << 8 | src[i + 1]) + 1
                            i += 2
                    if disp > len(out):
                        raise DecodeError("BAD_OFFSET", f"LZ back-reference {disp} beyond output {len(out)}")
                    for _ in range(length):
                        out.append(out[-disp])
                else:
                    out.append(src[i])
                    i += 1
    except IndexError:
        raise DecodeError("TRUNCATED", f"LZ stream ends at 0x{i:x} of 0x{n:x} with {len(out)}/{size} bytes") from None
    return bytes(out[:size])


def bgr555_to_rgb(v: int) -> tuple[int, int, int]:
    return ((v & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, ((v >> 10) & 31) * 255 // 31)
