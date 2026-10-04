#!/usr/bin/env python3
"""Validate the G7.2B message-box frame refresh (frames 1-5, palette-only)."""

import hashlib
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_message_frames as gen  # noqa: E402

WINDOWS = ROOT / "res" / "graphics" / "windows"

# SHA-256 of the retail pixel-index data (identical for frames 2-5).
INDEX_DIGESTS = {
    "message_box_00.png": "090ddee33b389501dac47f255cf0ef437f5246f44febf9ece4145816d5de6021",
    "message_box_01.png": "221fa21b523bf71a76c966d833be6daeed10ae386840060cbe9e1ca026a8bee7",
    "message_box_02.png": "221fa21b523bf71a76c966d833be6daeed10ae386840060cbe9e1ca026a8bee7",
    "message_box_03.png": "221fa21b523bf71a76c966d833be6daeed10ae386840060cbe9e1ca026a8bee7",
    "message_box_04.png": "221fa21b523bf71a76c966d833be6daeed10ae386840060cbe9e1ca026a8bee7",
}
# Retail entries that must stay put: transparent key, text/shadow entries 1-10
# (entry 2 is per-frame), field fill/halo 15.
RETAIL_ENTRY_2 = {
    "message_box_00.png": (65, 49, 32),
    "message_box_01.png": (65, 65, 65),
    "message_box_02.png": (57, 57, 106),
    "message_box_03.png": (90, 49, 41),
    "message_box_04.png": (57, 74, 32),
}
failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


def lum(rgb):
    def chan(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast(a, b):
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def main():
    for name, gradient in gen.FRAMES.items():
        image = Image.open(WINDOWS / name)
        check(image.size == (48, 24) and image.mode == "P", f"{name}: size/mode changed")
        check(hashlib.sha256(image.tobytes()).hexdigest() == INDEX_DIGESTS[name],
              f"{name}: pixel indices changed (palette-only pass)")
        pal = image.getpalette()
        entry = lambda i: tuple(pal[i * 3:i * 3 + 3])  # noqa: E731

        check(entry(0) == (156, 213, 139), f"{name}: transparent key changed")
        check(entry(1) == (255, 255, 255) and entry(15) == (255, 255, 255),
              f"{name}: white entries 1/15 changed (text field would seam)")
        check(entry(2) == RETAIL_ENTRY_2[name], f"{name}: per-frame entry 2 changed")
        check(entry(3) == (197, 205, 205) and entry(4) == (123, 131, 139),
              f"{name}: entries 3/4 changed")
        check(entry(14) == gen.OUTLINE, f"{name}: outline is not the G7 navy")
        for index, rgb in gradient.items():
            check(entry(index) == rgb, f"{name}: gradient entry {index} is not the G7 value")

        # Gradient must run dark -> light toward the text field, and every step
        # must separate from the white field and from the outline.
        order = sorted(gradient, key=lambda i: lum(gradient[i]))
        darkest, mid, lightest = (gradient[i] for i in order)
        check(lum(darkest) < lum(mid) < lum(lightest), f"{name}: gradient not monotonic")
        check(contrast(darkest, (255, 255, 255)) >= 3.0, f"{name}: darkest gradient step too pale")
        check(contrast(gen.OUTLINE, darkest) >= 1.2, f"{name}: outline merges with gradient")
        check(contrast(gen.OUTLINE, (255, 255, 255)) >= 12.0, f"{name}: outline vs field contrast")

    if failures:
        print("G7.2B message frame validation FAILED:")
        for failure in failures:
            print(" -", failure)
        sys.exit(1)
    print("G7.2B message frame validation passed")


if __name__ == "__main__":
    main()
