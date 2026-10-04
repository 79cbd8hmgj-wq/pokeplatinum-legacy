#!/usr/bin/env python3
"""Validate the G7.1A battle command-center resources.

Checks
  * the committed pl_batt_bg.narc is exactly what the generator emits
  * archive structure (member count / kinds) is unchanged
  * every member the generator does not own is byte-identical to retail
    (pinned aggregate digest) -> tile art, tilemaps and cells are untouched
  * edited palettes keep their index contract (transparent key, accent,
    greys, black) and the command-bank ramps are monotonic in luminance
  * button label outlines keep >= 3:1 contrast against their button fill
  * the focus cursor keeps its 16x16 canvas
"""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_battle_command_ui as gen  # noqa: E402
from nitro_narc import nclr_colors, read_narc, write_narc  # noqa: E402

ROOT = gen.ROOT
UNTOUCHED_DIGEST = "2dce2114a16bdc46225cd790c900d52cd09d1d955a8dfd337cea4ba579fb3cbd"
RETAIL_KEEP = {0: 0x75CD, 1: 0x7FFF, 11: 0x7C2B, 12: 0x318C, 13: 0x4631, 15: 0x0000}

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


def lum(c15):
    def chan(v):
        v = v / 31.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = c15 & 31, (c15 >> 5) & 31, (c15 >> 10) & 31
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def shared_pal_colors():
    lines = (ROOT / "res/graphics/battle/interface/shared.pal").read_text().split("\n")[3:]
    cols = [tuple(int(v) for v in line.split()) for line in lines if line.strip()]
    return [gen.bgr555(c) for c in cols]


def main():
    members, fnt = read_narc(gen.NARC_PATH)
    check(len(members) == 342, f"member count {len(members)} != 342")

    expected = write_narc(gen.generate(members), fnt)
    check(expected == gen.NARC_PATH.read_bytes(), "pl_batt_bg.narc differs from generator output")

    touched = set(gen.build_palette_edits()) | {gen.DEFAULT_SPEED_MEMBER}
    digest = hashlib.sha256()
    for i, member in enumerate(members):
        if i in touched:
            check(member[:4] == b"RLCN", f"member {i} is not an NCLR")
            continue
        digest.update(i.to_bytes(2, "little"))
        digest.update(hashlib.sha256(member).digest())
    check(digest.hexdigest() == UNTOUCHED_DIGEST, "an unowned pl_batt_bg member changed")

    main_pal = nclr_colors(members[gen.PALETTE_MAIN])
    for bank in range(1, 5):
        base = bank * 16
        for index, value in RETAIL_KEEP.items():
            if index in (0, 1, 11, 12, 13, 15):
                check(main_pal[base + index] == value,
                      f"bank {bank} entry {index} changed ({main_pal[base + index]:#x})")
        ramp = [lum(main_pal[base + i]) for i in (2, 3, 4, 5, 6, 7, 8)]
        check(all(a > b for a, b in zip(ramp, ramp[1:])),
              f"bank {bank} ramp is not monotonic: {[round(v, 3) for v in ramp]}")

    for bank in range(1, 5):
        check(main_pal[bank * 16] == 0x75CD, f"bank {bank} transparent key changed")
    check(all(main_pal[i] == c for i, c in zip(range(0, 8), nclr_colors(members[0xF3])[0:8])),
          "bank 0 entries 0-7 diverge from terrain palettes")

    text = shared_pal_colors()
    for bank, outline_entry in ((1, 3), (2, 6), (3, 9), (4, 12)):
        fill = main_pal[bank * 16 + 5]
        ratio = contrast(text[2 * 16 + outline_entry], fill)
        check(ratio >= 3.0, f"label outline vs bank {bank} fill contrast {ratio:.2f} < 3")

    # Backdrop: field must stay clearly darker than the bands' edge lines.
    for member in {m[0] for m in gen.TERRAIN_DECKS}:
        colors = nclr_colors(members[member])
        check(lum(colors[12]) > lum(colors[11]) * 1.5,
              f"terrain palette {member:#x}: edge line not distinct from field")
        check(colors[:8] == nclr_colors(members[0xF3])[:8],
              f"terrain palette {member:#x}: entries 0-7 changed")

    try:
        from PIL import Image

        cursor = Image.open(ROOT / "res/graphics/battle/interface/cursor.png")
        check(cursor.size == (16, 16) and cursor.mode == "P", "cursor.png must stay 16x16 indexed")
    except ImportError:
        print("Pillow unavailable; skipped cursor.png check")

    if failures:
        print("G7.1A battle command UI validation FAILED:")
        for failure in failures:
            print(" -", failure)
        sys.exit(1)
    print("G7.1A battle command UI validation passed")


if __name__ == "__main__":
    main()
